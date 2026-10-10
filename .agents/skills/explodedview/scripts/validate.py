#!/usr/bin/env python3
"""Validate a 3D /explodedview page and render PNG previews.

Usage: python validate.py page.html [--out DIR] [--embed-poster]
Static checks: leftover {{placeholders}}, external resources (Google Fonts only in the handwritten style), raster <img> (only the
embedded data: poster is allowed), the #ev-spec JSON (valid, unique part numbers, shapes and materials known, order 1..N).
Browser checks (headless Chromium WebGL): JavaScript errors, sideways page scroll, the canvas is not blank, parts do not overlap
each other when exploded (3D bounding boxes), every part sits at its assembled position at 0% and at at+explode at 100%, the assembled
model fills >= 50% and the exploded >= 40% of the stage width, callout labels are on screen and do not overlap in the default view,
parts list rows / labels / sidebar rows match the spec, controls work (zoom, reset, isolate, hide, show all, x-ray, labels toggle,
step through all parts, save image), the WebGL fallback is present (#nogl), and printing gives a light still of the exploded view
plus the parts list.
WARNS on: more than 14 parts, order gaps, reading-guide / step mismatch, parts that never move, labels hidden in the default view,
hard-coded colours, no icons, a file over 2.5 MB, no embedded poster.
Writes <name>_light.png, _dark.png, _mobile.png (the page as it opens: exploded), _assembled.png, _exploded.png and _print.pdf.
--embed-poster stores a still of the exploded view inside the page (for browsers without WebGL). Exit 1 on any FAIL.
"""
import re, sys, json, base64, pathlib, argparse
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

ap = argparse.ArgumentParser(); ap.add_argument("html"); ap.add_argument("--out", default=None); ap.add_argument("--embed-poster", action="store_true")
a = ap.parse_args()
src = pathlib.Path(a.html).resolve(); out = pathlib.Path(a.out or src.parent); out.mkdir(parents=True, exist_ok=True)
html = src.read_text(encoding="utf-8")
fails, warns = [], []

# ---------------------------------------------------------------- static checks (scripts and comments are not markup)
m_spec = re.search(r'<script[^>]*id="ev-spec"[^>]*>(.*?)</script>', html, re.S)
nohand = re.sub(r"<!--.*?-->", "", html, flags=re.S)
markup = re.sub(r"<script\b[^>]*>.*?</script>", "", nohand, flags=re.S)
markup = re.sub(r"<style\b[^>]*>.*?</style>", "", markup, flags=re.S)
hand = bool(re.search(r'data-style\s*=\s*"[^"]*hand', markup))
if re.search(r"\{\{[A-Z_]+\}\}", markup + (m_spec.group(1) if m_spec else "")): fails.append("unreplaced {{PLACEHOLDER}} left in file")
hosts = set(re.findall(r'(?:src|href)\s*=\s*["\']https?://([^/"\']+)', markup))
if re.search(r'<script\b[^>]*\bsrc\s*=', nohand): fails.append("external <script src> found - the three.js bundle must be inlined (see the template)")
if hand: hosts -= {"fonts.googleapis.com", "fonts.gstatic.com"}
if hosts: fails.append(f"external resources not allowed (page must be self-contained): {sorted(hosts)}")
for im in re.findall(r"<img\b[^>]*>", markup, re.I):
    if not re.search(r'\bsrc\s*=\s*"data:image/', im): fails.append("raster <img> that is not an embedded data: poster - build the model in the 3D spec")
hard = re.findall(r'(?:fill|stroke)\s*=\s*"(#[0-9a-fA-F]{3,8}|rgb[^"]*|(?:red|blue|green|black|white|orange|purple))"', markup)
if hard: warns.append(f"hard-coded colours in markup ({len(hard)}) - use .c0-.c5 classes so dark mode works")
ids = set(re.findall(r'\bid="([^"]+)"', markup))
refs = set(re.findall(r'(?:href|xlink:href)="#([^"]+)"', markup)) | set(re.findall(r'url\(#([^)]+)\)', markup))
missing = sorted(refs - ids)
if missing: fails.append(f"references to missing ids (icon names?): {missing}")
if not re.search(r'href="#i-', markup): warns.append("no icons used - the takeaway cards need icons (see SKILL.md)")
if len(html.encode()) > 2_500_000: warns.append("file over 2.5 MB")
if 'id="ev-partslist"' not in markup: warns.append('no <div id="ev-partslist"> - the parts list is written there from the spec (needed for print and the no-WebGL fallback)')
if 'class="ev-poster"' not in markup and not a.embed_poster: warns.append("no embedded poster for browsers without WebGL - run this validator with --embed-poster")
spec = None
if not m_spec: fails.append('no <script type="application/json" id="ev-spec"> found')
else:
    try: spec = json.loads(m_spec.group(1))
    except Exception as ex: fails.append(f"ev-spec is not valid JSON: {ex}")
if spec:
    ps = spec.get("parts") or []
    if not ps: fails.append("ev-spec has no parts")
    ns = [str(p.get("n")) for p in ps]
    if len(set(ns)) != len(ns): fails.append(f"duplicate part numbers in ev-spec: {sorted({n for n in ns if ns.count(n) > 1})}")
    for p in ps:
        for k in ("n", "name", "order", "shapes"):
            if k not in p: fails.append(f"part {p.get('n', '?')} has no '{k}'")
        if not p.get("shapes"): fails.append(f"part {p.get('n', '?')} has no shapes")
    if len(ps) > 14: warns.append(f"{len(ps)} parts - more than ~14 is hard to read; group small parts (screws) into one")
    ords = sorted({p.get("order") for p in ps if isinstance(p.get("order"), int)})
    if ords and ords != list(range(1, len(ords) + 1)): warns.append(f"order values {ords} are not 1..N without gaps")
    if sum(1 for p in ps if any(abs(v) > 1e-6 for v in (p.get("explode") or [0, 0, 0]))) < len(ps) - 1: warns.append("some parts have no 'explode' offset - they will not move (only the base part may stay)")
    steps = re.search(r'<ol[^>]*class="steps"[^>]*>(.*?)</ol>', markup, re.S)
    if steps:
        n_li = len(re.findall(r"<li\b", steps.group(1)))
        if n_li and n_li != len(ords): warns.append(f"{len(ords)} assembly orders but {n_li} steps written in the reading guide")
    for p in ps:
        if not p.get("role"): warns.append(f"part {p.get('n')} has no 'role' text (shown in the parts list and the tooltip)")

# ---------------------------------------------------------------- browser checks
GL_ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"]
SET = "([t]) => window.__ev3.set(t, true)"
PIX = """() => { const c = window.__ev3.canvas, t = document.createElement('canvas'); t.width = 160; t.height = Math.round(160 * c.height / c.width); const g = t.getContext('2d'); g.drawImage(c, 0, 0, t.width, t.height);
  const d = g.getImageData(0, 0, t.width, t.height).data; let on = 0, cols = new Set(); for (let i = 0; i < d.length; i += 4) { if (d[i + 3] > 40) { on++; cols.add((d[i] >> 5) + ',' + (d[i + 1] >> 5) + ',' + (d[i + 2] >> 5)); } }
  return { cover: on / (d.length / 4), colours: cols.size }; }"""
FILL = """() => { const e = window.__ev3, st = e.stage.getBoundingClientRect(); let x0 = 1e9, x1 = -1e9;
  e.parts.forEach(p => { const b = e.partBox(p); for (let i = 0; i < 8; i++) { const v = new b.min.constructor(i & 1 ? b.max.x : b.min.x, i & 2 ? b.max.y : b.min.y, i & 4 ? b.max.z : b.min.z); const q = e.project(v); x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); } });
  return (x1 - x0) / st.width; }"""
LABELS = """() => { const st = window.__ev3.stage.getBoundingClientRect(); return [...document.querySelectorAll('.ev-lab')].map(l => { const r = l.getBoundingClientRect(); return { n: l.dataset.n, off: l.classList.contains('off'), x: r.left - st.left, y: r.top - st.top, w: r.width, h: r.height, W: st.width, H: st.height }; }); }"""

def overlaps(boxes, tol):
    res = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            A, B = boxes[i], boxes[j]
            if all(min(A["max"][k], B["max"][k]) - max(A["min"][k], B["min"][k]) > tol for k in range(3)): res.append((A["n"], B["n"]))
    return res

def ready(pg):
    pg.evaluate("() => window.__evReady")
    pg.wait_for_function("() => document.documentElement.getAttribute('data-ev-ready')", timeout=30000)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=GL_ARGS)
    poster_uri = None
    for name, w, scheme in (("light", 1100, "light"), ("dark", 1100, "dark"), ("mobile", 390, "light")):
        pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1.25 if name != "mobile" else 2, color_scheme=scheme)
        errs = []
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
        pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" and "ERR_" not in m.text else None)
        pg.add_init_script(f"try {{ localStorage.setItem('vs-theme', '{scheme}'); }} catch (e) {{}}")   # the toggle stores the choice here
        pg.goto(src.as_uri())
        try: ready(pg)
        except Exception as ex: fails.append(f"{name}: the viewer did not start ({str(ex)[:80]}): {pg.evaluate('window.__evErrors')}"); pg.close(); continue
        pg.wait_for_timeout(900)
        if not pg.evaluate("() => !!(window.__ev3 && window.__ev3.webgl)"):
            fails.append(f"{name}: WebGL is not available in this browser (the 3D view cannot be checked)"); pg.close(); continue
        pg.evaluate("() => window.__ev3.render()"); pg.wait_for_timeout(250)
        if errs: fails.append(f"{name}: JavaScript errors: {errs[:3]}")
        for e in pg.evaluate("() => window.__evErrors || []"): fails.append(f"{name}: engine error: {e}")
        ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        if ov > 1: fails.append(f"{name}: page scrolls sideways by {ov}px")
        if name == "light":
            info = pg.evaluate("() => ({ n: window.__ev3.parts.length, pos: window.__ev3.pos(), N: window.__ev3.N })")
            if min(info["pos"]) < .99: warns.append("the page does not open fully exploded")
            px = pg.evaluate(PIX)
            if px["cover"] < .01 or px["colours"] < 6: fails.append(f"the 3D canvas looks blank (covered {px['cover']:.1%}, {px['colours']} colours)")
            # ---- DOM agreement: parts list rows, sidebar rows, labels
            rows = set(pg.evaluate("() => [...document.querySelectorAll('.ev-list tbody tr')].map(r => r.dataset.n)"))
            side = set(pg.evaluate("() => [...document.querySelectorAll('.ev-plist li')].map(r => r.dataset.n)"))
            labs = set(pg.evaluate("() => [...document.querySelectorAll('.ev-lab')].map(r => r.dataset.n)"))
            want = set(str(p["n"]) for p in (spec or {}).get("parts", []))
            for label, got in (("parts-list row", rows), ("sidebar row", side), ("callout label", labs)):
                for n in sorted(want - got, key=lambda s: (len(s), s)): fails.append(f"part {n} has no {label}")
                for n in sorted(got - want, key=lambda s: (len(s), s)): fails.append(f"{label} {n} has no part in the spec")
            # ---- exploded state
            pg.evaluate(SET, [1]); pg.wait_for_timeout(300); pg.evaluate("() => window.__ev3.render()")
            boxes = pg.evaluate("() => window.__ev3.boxes()")
            ext = max(max(bx["max"][k] for bx in boxes) - min(bx["min"][k] for bx in boxes) for k in range(3))
            for p1, p2 in overlaps(boxes, .004 * ext): fails.append(f"parts overlap each other when exploded (3D bounding boxes): {p1} x {p2}")
            fx = pg.evaluate(FILL)
            if fx < .40: fails.append(f"the exploded model fills only {fx:.0%} of the stage width (need >= 40%)")
            pos = pg.evaluate("() => window.__ev3.positions()")
            for q in pos:
                for k in range(3):
                    if abs(q["pos"][k] - (q["at"][k] + q["explode"][k])) > 1e-3: fails.append(f"part {q['n']} is not at at+explode when exploded"); break
            lab = pg.evaluate(LABELS); shown = [l for l in lab if not l["off"]]
            for l in lab:
                if l["off"]: warns.append(f"label {l['n']} is hidden in the default exploded view (its anchor is off screen) - set the part's 'label' point")
            for l in shown:
                if l["x"] < -1 or l["y"] < -1 or l["x"] + l["w"] > l["W"] + 1 or l["y"] + l["h"] > l["H"] + 1: fails.append(f"label {l['n']} sticks out of the stage")
            for i in range(len(shown)):
                for j in range(i + 1, len(shown)):
                    A, B = shown[i], shown[j]
                    if min(A["x"] + A["w"], B["x"] + B["w"]) - max(A["x"], B["x"]) > 2 and min(A["y"] + A["h"], B["y"] + B["h"]) - max(A["y"], B["y"]) > 2: fails.append(f"labels overlap: {A['n']} x {B['n']}")
            shot = out / f"{src.stem}_exploded.png"; pg.locator(".ev-stage").screenshot(path=str(shot)); print(f"rendered {shot}  (exploded)")
            if a.embed_poster: poster_uri = pg.evaluate("() => window.__ev3.poster()")
            # ---- assembled state
            pg.evaluate(SET, [0]); pg.wait_for_timeout(300); pg.evaluate("() => window.__ev3.render()")
            for q in pg.evaluate("() => window.__ev3.positions()"):
                for k in range(3):
                    if abs(q["pos"][k] - q["at"][k]) > 1e-3: fails.append(f"part {q['n']} does not sit at its assembled position at 0%"); break
            fa = pg.evaluate(FILL)
            if fa < .50: fails.append(f"the assembled model fills only {fa:.0%} of the stage width (need >= 50%)")
            shot = out / f"{src.stem}_assembled.png"; pg.locator(".ev-stage").screenshot(path=str(shot)); print(f"rendered {shot}  (assembled)")
            pg.evaluate(SET, [1]); pg.wait_for_timeout(200)
            for q in pg.evaluate("() => window.__ev3.positions()"):
                for k in range(3):
                    if abs(q["pos"][k] - (q["at"][k] + q["explode"][k])) > 1e-3: fails.append(f"part {q['n']} does not return to its exploded position"); break
            # ---- controls, programmatically
            d0 = pg.evaluate("window.__ev3.camDist()"); pg.evaluate("window.__ev3.zoomBy(.7)"); d1 = pg.evaluate("window.__ev3.camDist()")
            if not d1 < d0 * .9: fails.append("zoom in did not move the camera closer")
            pg.evaluate("window.__ev3.resetView()"); d2 = pg.evaluate("window.__ev3.camDist()")
            if abs(d2 - d0) > .05 * d0: fails.append("Reset view did not restore the framing")
            first, second = sorted(want, key=lambda s: (len(s), s))[:2]
            RATIO = "() => window.__ev3.parts.map(p => ({ n: p.n, r: p.meshes.filter(m => !m.userData.decal && m.userData.base).map(m => m.material.opacity / m.userData.base.opacity) }))"
            pg.evaluate("(n) => window.__ev3.isolate(n)", first)
            for q in pg.evaluate(RATIO):
                if q["n"] == first and q["r"] and max(q["r"]) < .5: fails.append("the isolated part is ghosted too")
                if q["n"] != first and q["r"] and max(q["r"]) > .2: fails.append(f"isolate did not ghost part {q['n']}"); break
            pg.evaluate("() => window.__ev3.isolate(null)")
            if any(q["r"] and min(q["r"]) < .9 for q in pg.evaluate(RATIO)): fails.append("restoring after isolate left parts ghosted")
            pg.evaluate("(n) => window.__ev3.hide(n, true)", second)
            if pg.evaluate("(n) => window.__ev3.parts.find(p => p.n === n).meshes.some(m => m.visible)", second): fails.append("hide did not hide the part")
            pg.evaluate("() => window.__ev3.showAll()")
            if not pg.evaluate("(n) => window.__ev3.parts.find(p => p.n === n).meshes.every(m => m.visible)", second): fails.append("Show all did not restore the part")
            pg.evaluate("() => window.__ev3.setXray(true)")
            if any(q["r"] and max(q["r"]) > .5 for q in pg.evaluate(RATIO)): fails.append("x-ray did not make the parts see-through")
            pg.evaluate("() => window.__ev3.setXray(false)")
            pg.evaluate("() => window.__ev3.setLabels(false)")
            if not pg.evaluate("document.querySelector('.ev-stage').classList.contains('nolabels')"): fails.append("the labels toggle does nothing")
            pg.evaluate("() => window.__ev3.setLabels(true)")
            # ---- every step: parts with order <= k are assembled, the others wait exploded
            orders = pg.evaluate("() => window.__ev3.parts.map(p => p.order)"); pnums = pg.evaluate("() => window.__ev3.parts.map(p => p.n)")
            for k in range(1, max(orders) + 1):
                pg.evaluate("(k) => { window.__ev3.step(k); }", k); pg.wait_for_timeout(1250)
                st = pg.evaluate("() => window.__ev3.pos()")
                bad = [i for i, (o, e) in enumerate(zip(orders, st)) if (o <= k and e > .02) or (o > k and e < .98)]
                if bad: fails.append(f"step {k}: parts {[pnums[i] for i in bad]} are not in the right place"); break
                lab_txt = pg.evaluate("document.querySelector('.ev-stepn').textContent")
                if f"Step {k} /" not in lab_txt: fails.append(f"the step bar says '{lab_txt}' at step {k}"); break
            pg.evaluate("() => { window.__ev3.step(0); window.__ev3.set(1, true); }"); pg.wait_for_timeout(300)
            cap = pg.evaluate("() => { const c = window.__ev3.capture(); return c.toDataURL('image/png').length; }")
            if cap < 3000: fails.append("Save image produced an empty picture")
            # ---- fallback + print
            pg2 = b.new_page(viewport={"width": 900, "height": 800}); pg2.goto(src.as_uri() + "#nogl")
            pg2.wait_for_function("() => document.documentElement.getAttribute('data-ev-ready')", timeout=15000)
            fb = pg2.evaluate("() => { const f = document.querySelector('.ev-fallback'); return { shown: !!f && !f.hidden, text: f ? f.textContent.trim().length : 0, img: !!(f && f.querySelector('img')), rows: document.querySelectorAll('.ev-list tbody tr').length, steps: document.querySelectorAll('ol.steps > li').length }; }")
            if not fb["shown"] or not (fb["text"] or fb["img"]): fails.append("without WebGL the page shows no fallback (poster or message)")
            if fb["rows"] < len(want) or not fb["steps"]: fails.append("without WebGL the parts list or the assembly steps are missing")
            pg2.close()
            pg.evaluate(SET, [0]); pg.emulate_media(media="print"); pg.wait_for_timeout(600)
            pr = pg.evaluate("() => ({ img: (document.querySelector('.ev-printimg').src || '').slice(0, 22), disp: getComputedStyle(document.querySelector('.ev-printimg')).display, canvas: getComputedStyle(window.__ev3.canvas).display, ctrl: getComputedStyle(document.querySelector('.ev-ctrl')).display, side: getComputedStyle(document.querySelector('.ev-side')).display, list: !!document.querySelector('.ev-list') && getComputedStyle(document.querySelector('.ev-list')).display !== 'none', bg: getComputedStyle(document.body).backgroundColor, ink: getComputedStyle(document.querySelector('h1')).color, pos: window.__ev3.pos() })")
            lum = lambda s: sum(int(v) for v in re.findall(r'\d+', s)[:3]) / 3
            if not pr["img"].startswith("data:image/png") or pr["disp"] == "none": fails.append("print layout has no still image of the exploded view")
            if pr["canvas"] != "none" or pr["ctrl"] != "none" or pr["side"] != "none": fails.append("print layout still shows the live canvas or the controls")
            if not pr["list"]: fails.append("print layout has no parts list")
            if lum(pr["bg"]) < 200 or lum(pr["ink"]) > 120: fails.append(f"print layout is not light (background {pr['bg']}, headline {pr['ink']})")
            pdf = out / f"{src.stem}_print.pdf"
            try: pg.pdf(path=str(pdf), format="A4", print_background=True); print(f"rendered {pdf}  (print)")
            except Exception as ex: warns.append(f"could not write the print PDF: {ex}")
            pg.emulate_media(media="screen"); pg.wait_for_timeout(300)
            pg.evaluate(SET, [1]); pg.evaluate("() => window.__ev3.resetView()"); pg.wait_for_timeout(500)
        pg.evaluate("() => { window.__ev3.set(1, true); window.__ev3.render(); }"); pg.wait_for_timeout(300)
        shot = out / f"{src.stem}_{name}.png"
        pg.screenshot(path=str(shot), full_page=True)
        print(f"rendered {shot}  ({w}px wide, {scheme})")
        pg.close()
    b.close()

if a.embed_poster and poster_uri and "FAIL" not in "".join(fails):
    img = f'<img class="ev-poster" alt="Exploded view (still image)" src="{poster_uri}">'
    html2 = re.sub(r'<img class="ev-poster"[^>]*>', "", html)
    html2 = html2.replace("</figure>", "  " + img + "\n</figure>", 1) if "</figure>" in html2 else html2
    src.write_text(html2, encoding="utf-8"); print(f"embedded poster ({len(poster_uri) // 1024} KB)")

for w_ in warns: print("WARN:", w_)
for f in fails: print("FAIL:", f)
print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
