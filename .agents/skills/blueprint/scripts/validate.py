#!/usr/bin/env python3
"""Validate a /blueprint page and render previews.

Usage: python validate.py drawing.html [--out DIR]
FAILS on: leftover {{placeholders}} or the CONTENT marker, external resources (Google Fonts are allowed only for the
handwritten style), unknown icon ids, no <svg class="bp-sheet">, no title block, JavaScript errors, sideways page scroll,
labels clipped by the sheet border or overlapping each other / a balloon / the title block / a notes box, balloons that
overlap, a balloon number with no parts-list row (or a row with no balloon), a dimension or balloon with missing or invalid
data, hover that does not link balloon <-> parts-list row, toggle buttons that do nothing, and a print layout that is not
light or still shows the controls.
WARNS on: no scale stated, a view without a label, no dimensions or no balloons, a dimension text that does not match its
drawn length, steps that do not match the data-step groups, more than 1 printed A4 page, a portrait print page, no scroll
hint, hard-coded colours in the drawing.
Writes <name>_light.png (Whiteprint), <name>_dark.png (Blueprint), <name>_mobile.png and <name>_print.pdf (print media, A4;
the page asks for landscape) and prints the printed page count. Exit 1 on any FAIL.
"""
import re, sys, pathlib, argparse
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

MAX_PAGES = 1        # printed pages (A4) before the drawing counts as too long

ap = argparse.ArgumentParser(); ap.add_argument("html"); ap.add_argument("--out", default=None)
a = ap.parse_args()
src = pathlib.Path(a.html).resolve(); out = pathlib.Path(a.out or src.parent); out.mkdir(parents=True, exist_ok=True)
html = src.read_text(encoding="utf-8")
fails, warns = [], []

# ---------- static checks ----------
if re.search(r"\{\{[A-Z_]+\}\}", html): fails.append("unreplaced {{PLACEHOLDER}} left in file")
if "CONTENT GOES HERE" in html: fails.append("the 'CONTENT GOES HERE' marker is still in the file")
hand = bool(re.search(r'data-style="handwritten"', html))
fonts = {"fonts.googleapis.com", "fonts.gstatic.com"}
hosts = set(re.findall(r'(?:src|href)\s*=\s*["\']https?://([^/"\']+)', html))
bad_hosts = hosts - fonts
if bad_hosts: fails.append(f"external resources not allowed (page must be self-contained): {sorted(bad_hosts)}")
if hosts & fonts and not hand: fails.append("Google Fonts link in a page that is not handwritten style (the default style is fully offline)")
if re.search(r"<img\b", html, re.I): fails.append("raster <img> found - draw the object in SVG")
m = re.search(r"<main\b.*?</main>", html, re.S); body = m.group(0) if m else html
if not re.search(r'<svg[^>]*class="[^"]*\bbp-sheet\b', body): fails.append('no <svg class="bp-sheet"> drawing found')
if 'bp-titleblock' not in body: fails.append('no title block: add <g class="bp-titleblock" data-title=... data-scale=...></g>')
known = set(re.findall(r'<symbol id="i-([^"]+)"', html))
used = set(re.findall(r'<use\s+href="#i-([^"]+)"', body))
if used - known: fails.append(f"unknown icon ids: {sorted(used - known)} (see SKILL.md list)")
sheet_markup = re.search(r'<svg[^>]*class="[^"]*\bbp-sheet\b.*?</svg>', body, re.S)
if sheet_markup and re.search(r'(?:fill|stroke)\s*=\s*"(#[0-9a-fA-F]{3,8}|rgb[^"]*|red|blue|green|black|white|orange|purple)"', sheet_markup.group(0)):
    warns.append("hard-coded colours in the drawing - use the bp-* classes so Blueprint / Whiteprint both work")
if len(html.encode()) > 2_000_000: warns.append("file over 2 MB")

# ---------- in-page checks ----------
JS = r"""(mode) => {
 const r = {errors: (window.__bpErrors || ['page script did not run']).slice(), issues: [], warns: (window.__bpWarnings || []).slice()};
 r.overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
 const svg = document.querySelector('svg.bp-sheet');
 if (!svg) { r.height = document.documentElement.scrollHeight; return r; }
 const vb = svg.viewBox.baseVal, M = 18;
 const inv = svg.getScreenCTM().inverse();
 const box = el => {                                   // bbox in the svg's own user space (handles transforms)
   const b = el.getBBox(), m = inv.multiply(el.getScreenCTM());
   const pts = [[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y]) => new DOMPoint(x,y).matrixTransform(m));
   const xs = pts.map(p=>p.x), ys = pts.map(p=>p.y);
   return {x:Math.min(...xs), y:Math.min(...ys), w:Math.max(...xs)-Math.min(...xs), h:Math.max(...ys)-Math.min(...ys)};
 };
 const shown = el => { const b = el.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
 const inter = (A, B, mx, my) => Math.min(A.x+A.w, B.x+B.w) - Math.max(A.x, B.x) > mx && Math.min(A.y+A.h, B.y+B.h) - Math.max(A.y, B.y) > my;
 const name = t => '"' + t.textContent.trim().slice(0, 24) + '"';
 // --- every dimension / balloon was drawn ---
 svg.querySelectorAll('g.bp-dim').forEach(g => { if (!g.firstChild) r.issues.push('a dimension was not drawn (missing data)'); });
 svg.querySelectorAll('g.bp-balloon').forEach(g => { if (!g.firstChild) r.issues.push('balloon ' + (g.dataset.n || '?') + ' was not drawn (missing data)'); });
 // --- texts: inside the border, not overlapping each other ---
 const hand = document.documentElement.classList.contains('hand');   // handwriting fonts have very tall line boxes: use the middle 60 %
 const tbox = t => { const b = box(t); return hand ? {x: b.x, y: b.y + b.h * 0.2, w: b.w, h: b.h * 0.6} : b; };
 const texts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim() && shown(t) && !t.classList.contains('bp-zt')).map(t => ({t, b: tbox(t)}));
 texts.forEach(({t, b}) => {
   if (b.x < M - 1 || b.y < M - 1 || b.x + b.w > vb.width - M + 1 || b.y + b.h > vb.height - M + 1) r.issues.push('label clipped by / outside the sheet border: ' + name(t));
 });
 for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
   const A = texts[i], B = texts[j];
   if (inter(A.b, B.b, 1.5, 0.25 * Math.min(A.b.h, B.b.h))) r.issues.push('labels overlap: ' + name(A.t) + ' x ' + name(B.t));
 }
 // --- balloons: no overlaps with each other, with labels, with the title block or notes ---
 const balls = [...svg.querySelectorAll('g.bp-balloon')].map(g => { const c = g.querySelector('circle.bp-bc'); return c ? {g, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')} : null; }).filter(Boolean);
 for (let i = 0; i < balls.length; i++) for (let j = i + 1; j < balls.length; j++)
   if (Math.hypot(balls[i].x - balls[j].x, balls[i].y - balls[j].y) < balls[i].r + balls[j].r - 1) r.issues.push('balloons overlap: ' + balls[i].g.dataset.n + ' and ' + balls[j].g.dataset.n);
 balls.forEach(bl => texts.forEach(({t, b}) => {
   if (bl.g.contains(t)) return;
   const cx = Math.max(b.x, Math.min(bl.x, b.x + b.w)), cy = Math.max(b.y, Math.min(bl.y, b.y + b.h));
   if (Math.hypot(cx - bl.x, cy - bl.y) < bl.r - 1) r.issues.push('balloon ' + bl.g.dataset.n + ' covers a label: ' + name(t));
 }));
 const blocks = [...svg.querySelectorAll('g.bp-titleblock, g.bp-notes')].filter(shown);
 blocks.forEach(blk => {
   const bb = box(blk.querySelector('rect') || blk), tag = blk.classList.contains('bp-titleblock') ? 'title block' : 'notes box';
   if (bb.x < M - 1 || bb.y < M - 1 || bb.x + bb.w > vb.width - M + 1 || bb.y + bb.h > vb.height - M + 1) r.issues.push(tag + ' sticks out of the sheet border');
   texts.forEach(({t, b}) => { if (!blk.contains(t) && inter(bb, b, 1, 1)) r.issues.push('label ' + name(t) + ' overlaps the ' + tag); });
   balls.forEach(bl => { if (inter(bb, {x: bl.x - bl.r, y: bl.y - bl.r, w: 2 * bl.r, h: 2 * bl.r}, 1, 1)) r.issues.push('balloon ' + bl.g.dataset.n + ' overlaps the ' + tag); });
   blocks.forEach(o => { if (o !== blk && o.compareDocumentPosition(blk) & 2 && inter(bb, box(o.querySelector('rect') || o), 1, 1)) r.issues.push('title block and notes box overlap'); });
 });
 // --- title block ---
 const tb = svg.querySelector('g.bp-titleblock');
 r.titleblock = !!tb && tb.childNodes.length > 0;
 r.tbText = tb ? tb.textContent.replace(/\s+/g, ' ').trim() : '';
 // --- views ---
 const views = [...svg.querySelectorAll('g.bp-view')];
 r.views = views.length;
 views.forEach((v, i) => { if (!v.querySelector('.bp-viewlabel')) r.warns.push('view ' + (i + 1) + ' has no label (add a g.bp-viewlabel)'); });
 r.viewLabels = svg.querySelectorAll('g.bp-viewlabel').length;
 r.dims = svg.querySelectorAll('g.bp-dim').length;
 // --- balloons <-> parts list ---
 const bn = new Set(balls.map(b => b.g.dataset.n));
 const rows = [...document.querySelectorAll('.bp-bom tbody tr')];
 const rn = new Set(rows.map(tr => tr.dataset.part || (tr.cells[0] && tr.cells[0].textContent.trim())));
 r.balloons = bn.size; r.rows = rn.size; r.hasBom = !!document.querySelector('.bp-bom');
 if (bn.size && !r.hasBom) r.issues.push('balloons but no parts list (<table class="bp-bom">)');
 if (r.hasBom) {
   [...bn].filter(n => !rn.has(n)).forEach(n => r.issues.push('balloon ' + n + ' has no row in the parts list'));
   [...rn].filter(n => !bn.has(n)).forEach(n => r.issues.push('parts-list row ' + n + ' has no balloon in the drawing'));
   rows.forEach(tr => { if (!tr.dataset.part) r.issues.push('a parts-list row has no data-part (hover link will not work)'); });
 }
 // --- steps ---
 const stepsLi = document.querySelectorAll('ol.steps > li').length;
 const stepSet = new Set(); svg.querySelectorAll('[data-step]').forEach(e => e.dataset.step.split(/\s+/).forEach(s => stepSet.add(s)));
 r.stepsLi = stepsLi; r.stepGroups = stepSet.size;
 if (stepsLi && !stepSet.size) r.warns.push('reading guide has steps but no element has data-step: the walkthrough will highlight nothing');
 if (!stepsLi && stepSet.size) r.warns.push('elements have data-step but there is no ol.steps reading guide');
 for (let i = 1; i <= stepsLi; i++) if (stepSet.size && !stepSet.has(String(i))) r.warns.push('step ' + i + ' of the reading guide has no data-step="' + i + '" element');
 [...stepSet].filter(s => +s > stepsLi).forEach(s => r.warns.push('data-step="' + s + '" but the reading guide has only ' + stepsLi + ' steps'));
 r.hint = (() => { const h = document.querySelector('.scroll-hint'); return !!h && getComputedStyle(h).display !== 'none'; })();
 r.stageScrolls = (() => { const s = document.querySelector('.stage'); return !!s && s.scrollWidth > s.clientWidth + 1; })();
 r.height = document.documentElement.scrollHeight;
 return r;
}"""

DARK_PATTERN = "try { localStorage.setItem('vs-theme', '%s'); } catch (e) {}"
req_hosts = set()
pdf_path = out / f"{src.stem}_print.pdf"
pages = None

PRINT_JS = r"""() => {
 const lum = c => { const m = c.match(/[\d.]+/g).map(Number); return (m[0] + m[1] + m[2]) / 3; };
 const d = e => e ? getComputedStyle(e).display : 'none';
 const tb = document.querySelector('svg.bp-sheet g.bp-titleblock');
 const paper = document.querySelector('svg.bp-sheet .bp-paper');
 const r = tb ? tb.getBoundingClientRect() : null, s = document.querySelector('svg.bp-sheet').getBoundingClientRect();
 return {bgL: lum(getComputedStyle(document.body).backgroundColor), inkL: lum(getComputedStyle(document.body).color),
   paperL: paper ? lum(getComputedStyle(paper).fill.startsWith('rgb') ? getComputedStyle(paper).fill : 'rgb(255,255,255)') : 255,
   toggle: d(document.querySelector('.theme-toggle')), bar: d(document.querySelector('.bp-bar')), player: d(document.querySelector('.player')),
   tbVisible: !!r && r.width > 20 && r.height > 20 && r.right <= s.right + 1 && r.bottom <= s.bottom + 1, svgW: s.width, svgH: s.height};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, scheme in (("light", 1100, "light"), ("dark", 1100, "dark"), ("mobile", 390, "light")):
        pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=1.5, color_scheme=scheme)
        # pages open in Deep dark (Blueprint) and ignore the OS setting; the sun/moon toggle stores the choice here
        pg.add_init_script(DARK_PATTERN % ("light" if name != "dark" else "dark"))
        js_errors = []
        pg.on("pageerror", lambda e: js_errors.append(str(e)))
        pg.on("request", lambda rq: req_hosts.add(rq.url.split("/")[2]) if rq.url.startswith("http") else None)
        pg.goto(src.as_uri()); pg.wait_for_timeout(300)
        pg.evaluate("() => window.__bpReady")   # handwriting fonts (if any) are loaded first
        pg.wait_for_timeout(300)
        if name == "light" and pg.evaluate("document.documentElement.classList.contains('hand')") \
                and not pg.evaluate("document.fonts.check('16px Kalam')"):
            warns.append("handwriting web font not loaded (offline?) - fallback font in use")
        r = pg.evaluate(JS, "screen")
        if js_errors: fails.append(f"{name}: JavaScript error: {js_errors[0]}")
        if r["overflow"] > 1: fails.append(f"{name}: page scrolls sideways by {r['overflow']}px")
        if name == "light":
            fails += sorted(set(r["errors"]))
            fails += [f"{i}" for i in sorted(set(r["issues"]))[:12]]
            warns += sorted(set(r["warns"]))
            if not r["titleblock"]: fails.append("title block is empty or missing")
            elif not re.search(r"scale", r["tbText"], re.I): warns.append("no scale in the title block")
            if r["views"] == 0: warns.append("no <g class=\"bp-view\"> groups: wrap each view (and its data-k scale) in one")
            if r["dims"] == 0: warns.append("no dimensions (g.bp-dim) in the drawing")
            if r["balloons"] == 0: warns.append("no balloons (g.bp-balloon) in the drawing")
            # interaction: hover balloon <-> row, layer toggles
            if r["balloons"] and r["hasBom"]:
                n_ = pg.evaluate("document.querySelector('g.bp-balloon[data-part]').dataset.part")
                pg.hover(f"g.bp-balloon[data-part='{n_}'] text.bp-bt"); pg.wait_for_timeout(120)
                row_on = pg.evaluate(f"document.querySelector('.bp-bom tbody tr[data-part=\"{n_}\"]').classList.contains('hl')")
                if not row_on: fails.append(f"hover: hovering balloon {n_} does not highlight its parts-list row")
                pg.mouse.move(2, 2); pg.wait_for_timeout(80)
                pg.hover(f".bp-bom tbody tr[data-part='{n_}']"); pg.wait_for_timeout(120)
                ball_on = pg.evaluate(f"document.querySelector('g.bp-balloon[data-part=\"{n_}\"]').classList.contains('hl')")
                if not ball_on: fails.append(f"hover: hovering parts-list row {n_} does not highlight its balloon")
                pg.mouse.move(2, 2)
            for bid, sel, label in (("bp-dims", "svg.bp-sheet g.bp-dim", "Dimensions"), ("bp-hidden", "svg.bp-sheet .bp-hidden", "Hidden lines")):
                if pg.query_selector(f"#{bid}") and pg.query_selector(sel):
                    pg.click(f"#{bid}"); pg.wait_for_timeout(80)
                    off = pg.evaluate(f"getComputedStyle(document.querySelector('{sel}')).display") == "none"
                    pg.click(f"#{bid}"); pg.wait_for_timeout(80)
                    on = pg.evaluate(f"getComputedStyle(document.querySelector('{sel}')).display") != "none"
                    if not off or not on: fails.append(f"toggle: the '{label}' button does not hide / show its layer")
        if name == "mobile":
            if r["stageScrolls"] and not r["hint"]: warns.append("mobile: the drawing scrolls sideways but there is no scroll hint (<p class=\"scroll-hint\">)")
        shot = out / f"{src.stem}_{name}.png"
        pg.screenshot(path=str(shot), full_page=True)
        print(f"rendered {shot}  ({w}px wide, {'whiteprint' if name != 'dark' else 'blueprint'}, {r['height']}px tall)")
        if name == "dark":
            # print must be the light Whiteprint look even though the screen theme is dark
            pg.emulate_media(media="print"); pg.wait_for_timeout(200)
            pr = pg.evaluate(PRINT_JS)
            if pr["bgL"] < 235: fails.append("print: page background is not light")
            if pr["inkL"] > 110: fails.append("print: text colour is not dark")
            if pr["paperL"] < 225: fails.append("print: the drawing sheet is not light paper (Whiteprint)")
            if pr["toggle"] != "none" or pr["bar"] != "none": fails.append("print: the theme toggle / layer buttons are still visible")
            if pr["player"] != "none": fails.append("print: the walkthrough player is still visible")
            if not pr["tbVisible"]: fails.append("print: the title block is not visible inside the sheet")
            pg.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
            data = pdf_path.read_bytes()
            pages = len(re.findall(rb"/Type\s*/Page(?![s\w])", data)) or None
            mb = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", data)
            land = None
            if mb: land = float(mb.group(3)) - float(mb.group(1)) > float(mb.group(4)) - float(mb.group(2))
            print(f"rendered {pdf_path}  (A4, print media, {pages} page(s), {'landscape' if land else 'portrait' if land is False else '?'})")
            if pages and pages > MAX_PAGES: warns.append(f"prints on {pages} A4 pages - a drawing should fit one page: shorten the notes / parts list or lower the sheet height")
            if land is False: warns.append("print page is portrait - the drawing should print landscape (@page size A4 landscape)")
        pg.close()
    b.close()

if req_hosts - fonts - {""}: fails.append(f"the page requested external hosts at runtime: {sorted(req_hosts - fonts)}")
for w_ in warns: print("WARN:", w_)
for f in fails: print("FAIL:", f)
print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})", f"| printed pages: {pages}")
sys.exit(1 if fails else 0)
