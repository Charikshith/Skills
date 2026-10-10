#!/usr/bin/env python3
"""Validate an /xray page and render PNG previews.

Usage: python validate.py xray.html [--out DIR]
Checks: leftover {{placeholders}}, external resources (Google Fonts only for the handwritten style),
unknown icon / marker / path ids, JavaScript errors, sideways page scroll at desktop and phone width,
SVG labels clipped outside the viewBox, labels or cards overlapping, a missing .xr-outside or .xr-inside
layer, a scanner that does not work (it moves the scanner by code and by keyboard and checks that the
clip changes, and that the mode switch and lens work), a print layout that is not light or hides the
inside layer. Warns on parts without labels, label steps that have no reading-guide step, badge/step
mismatch, no motion, no scan grid, hard-coded colours.
Photo support: an <image class="xr-photo"> may use a relative file or a data: URI (a missing file FAILS).
Look: data-look="scan" (default) or "color"; tone: data-tone="cyan" (default) or "film".
Writes <name>_light.png, <name>_dark.png, <name>_mobile.png and <name>_xray.png (dark, scanner
fully revealing the inside). Exit 1 on any FAIL.
"""
import re, sys, pathlib, argparse
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

ap = argparse.ArgumentParser(); ap.add_argument("html"); ap.add_argument("--out", default=None)
a = ap.parse_args()
src = pathlib.Path(a.html).resolve(); out = pathlib.Path(a.out or src.parent); out.mkdir(parents=True, exist_ok=True)
html = src.read_text(encoding="utf-8")
fails, warns = [], []

hand = bool(re.search(r'<figure[^>]*data-style="handwritten"', html))
if re.search(r"\{\{[A-Z_]+\}\}", html): fails.append("unreplaced {{PLACEHOLDER}} left in file")
hosts = set(re.findall(r'(?:src|href)\s*=\s*["\']https?://([^/"\']+)', html))
fonts = {"fonts.googleapis.com", "fonts.gstatic.com"}
if hosts & fonts and not hand: fails.append("Google Fonts link in a page that is not handwritten style (the clean style is fully offline)")
hosts_bad = hosts - (fonts if hand else set())
if re.search(r'url\(\s*["\']?https?://', html): hosts_bad = hosts_bad | {"url(http…) in CSS/SVG"}
if hosts_bad: fails.append(f"external resources not allowed (page must be self-contained): {sorted(hosts_bad)}")
if re.search(r'<img\b', html, re.I): fails.append("raster <img> found - use an SVG <image class=\"xr-photo\"> inside .xr-outside for a photo")
# attached photo: <image class="xr-photo" href="relative-file.png | data:..."> (no http/https); a local file must exist
photos = re.findall(r'<image\b[^>]*?(?:xlink:)?href\s*=\s*["\']([^"\']+)["\'][^>]*>', html)
for ph in photos:
    if ph.startswith("data:image/"): continue
    if re.match(r'^[a-z]+:', ph, re.I) or ph.startswith("//"): fails.append(f"photo '{ph[:60]}' is not a local file or data: URI"); continue
    if not (src.parent / ph).is_file(): fails.append(f"photo file not found next to the page: {ph}")
if photos and not re.search(r'<image\b[^>]*class="[^"]*\bxr-photo\b', html): warns.append("<image> without class=\"xr-photo\" - the x-ray filter will not be applied")
if photos and not re.search(r'class="[^"]*\bxr-outside\b[^"]*"[^>]*>\s*(?:<!--.*?-->\s*)*<image', html, re.S): warns.append("the photo should be the first thing inside <g class=\"xr-outside\">")
if re.search(r'data-look="(?!scan"|color")', html): fails.append('data-look must be "scan" (default) or "color"')
if re.search(r'data-tone="(?!cyan"|film")', html): fails.append('data-tone must be "cyan" (default) or "film" (the default when a photo is attached)')
if re.search(r'class="[^"]*\bxr-photo-xray\b', html) and not re.search(r'class="[^"]*\bxr-photo\b(?!-)', html): warns.append("xr-photo-xray (inside) without an original xr-photo (outside): the Outside view will show no photo")
body = html.split("<main", 1)[-1].split("<script>")[0]          # the content, without the page scripts
hard = re.findall(r'(?:fill|stroke)\s*=\s*"(#[0-9a-fA-F]{3,8}|rgb[^"]*|(?:red|blue|green|black|white|orange|purple))"', body)
if hard: warns.append(f"hard-coded colours in markup ({len(hard)}) - use .c1-.c5 classes so dark mode works")
ids = set(re.findall(r'\bid="([^"]+)"', html))
refs = set(re.findall(r'(?:href|xlink:href)="#([^"]+)"', body)) | set(re.findall(r'url\(#([^)]+)\)', body))
missing = sorted(refs - ids)
if missing: fails.append(f"references to missing ids (icon/marker/path names?): {missing}")
if not re.search(r'href="#i-', body): warns.append("no icons used - give label cards an icon chip (see SKILL.md)")
if not re.search(r'class="[^"]*\b(flow|particle)\b', body): warns.append("no motion - add .flow dashes or a .particle on a path inside the object")
if not re.search(r'data-step="', body): warns.append("no data-step groups - step highlighting and the walkthrough will do nothing")
if not re.search(r'class="[^"]*\bxr-outside\b', body): fails.append("no <g class=\"xr-outside\"> layer (the outside view)")
if not re.search(r'class="[^"]*\bxr-inside\b', body): fails.append("no <g class=\"xr-inside\"> layer (the hidden parts)")
if not re.search(r'class="[^"]*\bxr-scan\b', body): warns.append("no .xr-scan grid rectangle - the scanner look is flatter without it")
if not re.search(r'class="[^"]*\bxr-shell\b', body): warns.append("no .xr-shell silhouette on the outside layer")
if len(html.encode()) > 2_000_000: warns.append("file over 2 MB")

JS = r"""() => {
 const r = {};
 r.overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
 r.clipped = []; r.overlaps = []; r.cardOverlaps = [];
 document.querySelectorAll('figure > svg').forEach((svg, i) => {
   const vb = svg.viewBox.baseVal; if (!vb || !vb.width) return;
   const boxes = [], inv = svg.getScreenCTM().inverse();
   const bbox = el => {
     const b = el.getBBox(), m = inv.multiply(el.getScreenCTM());
     const pts = [[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]
       .map(([x,y]) => new DOMPoint(x,y).matrixTransform(m));
     const xs = pts.map(p=>p.x), ys = pts.map(p=>p.y);
     return {x:Math.min(...xs), y:Math.min(...ys), width:Math.max(...xs)-Math.min(...xs), height:Math.max(...ys)-Math.min(...ys)};
   };
   svg.querySelectorAll('text').forEach(t => {
     const b = bbox(t);
     if (b.x < vb.x - 2 || b.y < vb.y - 2 || b.x + b.width > vb.x + vb.width + 2 || b.y + b.height > vb.y + vb.height + 2)
       r.clipped.push(`fig${i+1}: "${t.textContent.trim().slice(0,30)}"`);
     if (!t.closest('.badge')) boxes.push([t.textContent.trim().slice(0,24), b]);
   });
   const ov = (A,B) => [Math.min(A.x+A.width,B.x+B.width)-Math.max(A.x,B.x), Math.min(A.y+A.height,B.y+B.height)-Math.max(A.y,B.y)];
   for (let j=0;j<boxes.length;j++) for (let k=j+1;k<boxes.length;k++){
     const A=boxes[j][1], B=boxes[k][1], [ox,oy]=ov(A,B);
     if (ox>2 && oy>0.3*Math.min(A.height,B.height)) r.overlaps.push(`fig${i+1}: "${boxes[j][0]}" x "${boxes[k][0]}"`);
   }
   // text must sit inside its own card
   svg.querySelectorAll('.xr-labels .lift, .xr-label .lift').forEach(g => {
     const rect = g.querySelector('rect.node'); if (!rect) return;
     const R = bbox(rect);
     g.querySelectorAll('text').forEach(t => { const b = bbox(t);
       if (b.x + b.width > R.x + R.width - 6 || b.x < R.x || b.y < R.y || b.y + b.height > R.y + R.height) r.clipped.push(`card text spills: "${t.textContent.trim().slice(0,28)}"`); });
   });
   const cards = [...svg.querySelectorAll('rect.node')].map(e => [e, bbox(e)]);
   for (let j=0;j<cards.length;j++) for (let k=j+1;k<cards.length;k++){
     const [ox,oy]=ov(cards[j][1],cards[k][1]); if (ox>2 && oy>2) r.cardOverlaps.push(`fig${i+1}: two label cards overlap`);
   }
 });
 r.badges = document.querySelectorAll('figure .badge').length;
 r.steps = document.querySelectorAll('ol.steps > li').length;
 r.labelSteps = [...document.querySelectorAll('.xr-label [data-step]')].flatMap(e => e.dataset.step.split(' ')).map(Number);
 r.partSteps = [...document.querySelectorAll('.xr-inside [data-step]')].flatMap(e => e.dataset.step.split(' ')).map(Number);
 r.labels = document.querySelectorAll('.xr-label').length;
 r.parts = document.querySelectorAll('.xr-inside .xr-part, .xr-inside .xr-tube, .xr-inside .xr-valve, .xr-inside .xr-line').length;
 r.height = document.documentElement.scrollHeight;
 return r;
}"""

def theme_page(b, w, scheme):
    pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1.5, color_scheme=scheme)
    pg.add_init_script(f"try {{ localStorage.setItem('vs-theme', '{scheme}'); }} catch (e) {{}}")
    return pg

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, scheme in (("light", 1100, "light"), ("dark", 1100, "dark"), ("mobile", 390, "light")):
        pg = theme_page(b, w, scheme)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "fonts" not in m.text.lower() and "ERR_" not in m.text else None)
        pg.on("requestfailed", lambda r: errs.append("resource failed to load: " + r.url[-60:]) if "fonts." not in r.url else None)
        pg.goto(src.as_uri()); pg.wait_for_timeout(500)
        pg.evaluate("() => window.__xrReady || true")
        if name == "light":
            fails += [f"JavaScript error: {e}" for e in errs]
            jserr = pg.evaluate("() => window.__xrErrors || []")
            fails += [f"x-ray script: {e}" for e in jserr]
        elif errs: fails += [f"JavaScript error ({name}): {e}" for e in errs[:2]]
        r = pg.evaluate(JS)
        if r["overflow"] > 1: fails.append(f"{name}: page scrolls sideways by {r['overflow']}px")
        if name == "light":
            fails += [f"label clipped outside viewBox - {c}" for c in r["clipped"]]
            fails += [f"labels overlap - {o}" for o in r["overlaps"]]
            fails += [f"label cards overlap - {o}" for o in r["cardOverlaps"]]
            if r["badges"] and r["steps"] and r["badges"] != r["steps"]:
                warns.append(f"{r['badges']} numbered badges in the visual but {r['steps']} steps in the reading guide")
            if r["parts"] and r["labels"] < 3: warns.append(f"{r['parts']} inside parts but only {r['labels']} label cards - every main part needs a labelled card")
            if r["parts"] == 0: warns.append("no .xr-part / .xr-tube / .xr-valve / .xr-line parts found in the inside layer")
            noL = sorted(set(r["partSteps"]) - set(r["labelSteps"]))
            if noL: warns.append(f"inside parts in step(s) {noL} have no labelled card")
            bad = sorted({s for s in r["labelSteps"] + r["partSteps"] if s < 1 or s > r["steps"]})
            if bad: warns.append(f"data-step values {bad} do not exist in the reading guide ({r['steps']} steps)")
            if r["steps"] < 3: warns.append("fewer than 3 reading-guide steps")
            noS = sorted(set(range(1, r["steps"] + 1)) - set(r["partSteps"]) - set(r["labelSteps"]))
            if noS: warns.append(f"reading-guide step(s) {noS} highlight nothing (no data-step={noS[0]} in the visual)")
            # ---- the scanner ----
            if not jserr:
                api = pg.evaluate("() => !!window.__xr")
                if not api: fails.append("scanner not built (window.__xr missing)")
                else:
                    init = pg.evaluate("() => __xr.state().scan")
                    pg.evaluate("() => { __xr.setLens(false); __xr.setMode('both'); __xr.setScan(0.2); }")
                    s1 = pg.evaluate("() => __xr.state()")
                    pg.evaluate("() => __xr.setScan(0.8)")
                    s2 = pg.evaluate("() => __xr.state()")
                    if not s2["clipWidth"] > s1["clipWidth"] + 20: fails.append(f"scanner does not change the clip (width {s1['clipWidth']:.0f} -> {s2['clipWidth']:.0f})")
                    if s2["labelsOn"] < s1["labelsOn"]: fails.append("moving the scanner right hides labels (they should appear)")
                    # keyboard on the handle
                    pg.focus(".xr-scanbar"); v0 = pg.evaluate("() => +document.querySelector('.xr-scanbar').getAttribute('aria-valuenow')")
                    pg.keyboard.press("ArrowLeft"); pg.keyboard.press("ArrowLeft"); pg.keyboard.press("Shift+ArrowLeft")
                    v1 = pg.evaluate("() => +document.querySelector('.xr-scanbar').getAttribute('aria-valuenow')")
                    if not v1 < v0: fails.append(f"arrow keys do not move the scanner ({v0} -> {v1})")
                    if not pg.evaluate("() => !!document.querySelector('.xr-bar input[type=range]')"): fails.append("no scanner slider in the toolbar")
                    # mode switch
                    pg.evaluate("() => __xr.setMode('outside')"); mo = pg.evaluate("() => __xr.state()")
                    pg.evaluate("() => __xr.setMode('xray')"); mx = pg.evaluate("() => __xr.state()")
                    if not (mo["clipWidth"] == 0 and mx["clipWidth"] > 300): fails.append(f"mode switch broken (outside clip {mo['clipWidth']}, x-ray clip {mx['clipWidth']})")
                    pg.click('.xr-bar [data-mode="both"]')
                    if pg.evaluate("() => __xr.state().mode") != "both": fails.append("the Both button does not switch the mode")
                    # lens
                    pg.evaluate("() => { __xr.setMode('outside'); __xr.setLens(true); }")
                    if pg.evaluate("() => +document.getElementById('xr-clip-lens').getAttribute('r')") <= 0: fails.append("lens does not reveal anything")
                    pg.evaluate("(f) => { __xr.setLens(false); __xr.setMode('both'); __xr.setScan(f); }", init); pg.wait_for_timeout(450)
        shot = out / f"{src.stem}_{name}.png"
        pg.screenshot(path=str(shot), full_page=True)
        print(f"rendered {shot}  ({w}px wide, {scheme}, {r['height']}px tall)")
        if name == "dark":   # the x-ray view: scanner fully revealing the inside
            if pg.evaluate("() => !!window.__xr"):
                pg.evaluate("() => __xr.setMode('xray')"); pg.wait_for_timeout(450)
                shot = out / f"{src.stem}_xray.png"
                pg.locator(".stage").screenshot(path=str(shot))
                print(f"rendered {shot}  (x-ray view, dark)")
        pg.close()
    # ---- print layout: light, inside layer shown, controls hidden ----
    pg = theme_page(b, 1100, "dark"); pg.goto(src.as_uri()); pg.wait_for_timeout(400)
    pg.emulate_media(media="print")
    pr = pg.evaluate("""() => { const q = s => document.querySelector(s), cs = el => el ? getComputedStyle(el) : null;
      const bg = cs(document.body).backgroundColor.match(/\\d+/g).map(Number);
      return {bg: Math.min(...bg.slice(0,3)), bar: cs(q('.xr-bar')) ? cs(q('.xr-bar')).display : 'none',
              clip: cs(q('.xr-inside')) ? cs(q('.xr-inside')).clipPath : 'none', surf: cs(q('.stage')).backgroundColor}; }""")
    if pr["bg"] < 225: fails.append("print: page background is not light")
    if pr["bar"] != "none": fails.append("print: the scanner toolbar is still shown")
    if pr["clip"] not in ("none", ""): fails.append(f"print: the inside layer is still clipped ({pr['clip']})")
    pg.close()
    b.close()

for w_ in warns: print("WARN:", w_)
for f in fails: print("FAIL:", f)
print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
