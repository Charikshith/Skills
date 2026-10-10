---
name: blueprint
description: Draw a detailed technical blueprint of an object, building, room, device or mechanism as a classic engineering-drawing page — a sheet with paper grid and border, multiple views (front / side / top, plan and elevation, detail views), line weights for outlines, hidden lines and centre lines, real dimension lines with arrowheads and extension lines, numbered callout balloons tied to a parts list (bill of materials), hatching, a title block (title, drawing number, scale, units, date, sheet) and a notes box. Dark = Blueprint (white lines on blue), light = Whiteprint (dark-blue lines on white) via the sun/moon button; hover a balloon or a parts-list row to light the part, toggle dimensions and hidden lines, play a walkthrough over the parts, prints on one landscape page, and an optional handwritten pencil-on-graph-paper style when asked. Use this whenever the user types /blueprint, or asks for a blueprint, technical drawing, engineering drawing, floor plan, elevation, "dimensioned drawing", orthographic views, schematic of a device, or "draw the plans for X", even if they don't say "blueprint". For parts pulled apart use /explodedview; for a general explainer visual use /visualize; for a process use /flowchart.
---

# /blueprint — any object or building → a dimensioned technical drawing

The output is ONE self-contained HTML page: an eyebrow, a headline, a lede, fact chips, a **layers toolbar**
(Dimensions, Hidden lines, Grid, Print / Save PDF), **one drawing sheet** (an SVG with paper, grid, border, 2–4 labelled
views, dimensions, balloons, notes box and title block) with a walkthrough player, a **parts list** keyed to the balloons,
a line-type legend, a numbered reading guide, 3 short notes and a footnote. No external assets (Google Fonts only in the
optional handwritten style).

It must look like a **real drawing** (clean line weights, legible dimensions, nothing overlapping) and it must be
**internally consistent**: the same size is never given two different values, areas add up, every balloon is in the parts
list, and plan and elevation agree.

**Page theme:** pages open in the **Blueprint** look (deep blue paper, white and cyan lines — this is the template's Deep
dark theme). A ☀/☾ button (built into the template, top right) switches to the **Whiteprint** look (white paper, dark-blue
lines, light grid) and remembers the choice; the device's own dark mode is ignored. Don't remove the button or add your own
theme CSS: every colour is a CSS variable, so the drawing repaints live. Check both themes (the validator renders both).
**Printing is always Whiteprint** (light), landscape, whichever theme is on screen: the template does it, hides the toolbar,
the toggle and the player, and puts the parts list beside the sheet so the whole drawing fits one A4 page.

## Usage
`/blueprint <object or building>` — optional extras: size or scale ("1:20"), views ("plan and elevation", "front and side"),
level ("simple", "detailed"), `handwritten`, language.
Defaults: orthographic views of the whole object (front + side + top, plus one detail), 8–12 parts, A3 sheet, metric.

If the user gives only `/blueprint` with no topic, ask for the topic in one short line.

## Step 1 — Plan the drawing (before any SVG)
- **Which views?** Object: FRONT, SIDE, TOP (first-angle: top view below the front view, side view beside it) and one
  DETAIL view of the most interesting joint, at a larger scale. Building or room: PLAN (north up) and one ELEVATION or SECTION.
  Mechanism: the view that shows the moving parts, plus a section if the inside matters. Give every view a letter and a title.
- **Real sizes.** Decide the real dimensions in mm (metres for buildings) first. They must be realistic for the thing, and
  every size the page prints must come from the geometry (see `data-k` below) — never typed separately from the drawing.
  **Say they are illustrative** (footnote, notes box and a chip) unless they come from a real, named specification.
- **Scale.** The sheet is 1000 × 700 units = an A3 sheet (1 unit = 0.42 mm on paper). At scale 1:S one unit is
  `k = 0.42 × S` real mm, so `data-k` = 0.42 × S (1:3 → 1.26, 1:25 → 10.5, 1:50 → 21) and a real size in mm is drawn as
  size ÷ k units. Different views may have different scales; each view group carries its own `data-k` and its label says its scale.
- **Parts list.** 8–12 numbered parts (rooms and fittings for a building). Each gets a name, a material or spec, a quantity.
  Every number appears as a balloon in at least one view and as a row in the table — and vice versa.
- **Layout.** Border zone is 18 units. Put views in a grid with ≥ 60 units between views for their dimensions and labels.
  Reserve the bottom-right (340 × 80) for the title block and put the notes box just above it. Aim for balanced white space.
- **Walkthrough steps (4–7).** Group parts into a build-up order (foundation → structure → moving parts → covers →
  fittings). Parts of one step share `data-step="N"`.
- **Chips (3–4):** number of parts, number of views, scale, "sizes illustrative".

## Step 2 — Build the page from the template
Copy `assets/template.html` (in this skill's folder). Replace `{{TITLE}}` (plain text), `{{HEADLINE}}` (may contain
`<span class="accent">`), `{{FORM}}` (e.g. `Blueprint · Product`), `{{LEDE}}` (≤ 25 words), and put the content where
`<!-- CONTENT GOES HERE -->` is. Don't edit the template's CSS or scripts. For anything beyond a few lines, **generate the
markup with a small script** (compute coordinates from real sizes) instead of typing numbers by hand.

```html
<ul class="chips"><li><b>11</b> parts</li><li>Scale <b>1:3</b> (A3)</li><li>Sizes <b>illustrative</b></li></ul>
<div class="bp-bar" role="group" aria-label="Drawing layers"><span class="bp-bar-lbl">Layers</span>
  <button class="bp-btn" id="bp-dims" type="button" aria-pressed="true">Dimensions</button>
  <button class="bp-btn" id="bp-hidden" type="button" aria-pressed="true">Hidden lines</button>
  <button class="bp-btn" id="bp-grid" type="button" aria-pressed="true">Grid</button>
  <button class="bp-btn plain" id="bp-print" type="button">Print / Save PDF</button></div>
<div class="bp-main">
  <figure class="stage bp-stage" id="bp-stage">
    <svg class="bp-sheet" viewBox="0 0 1000 700" data-unit="mm" role="img" aria-label="one-sentence description">
      <g class="bp-view" data-k="1.26"> … parts, dimensions, balloons, a g.bp-viewlabel … </g>
      <g class="bp-notes" …></g>
      <g class="bp-titleblock" …></g>
    </svg>
    <figcaption>What the reader is looking at. Hover a balloon or a row in the parts list.</figcaption>
  </figure>
  <p class="scroll-hint">&larr; swipe the drawing &rarr;</p>
  <div class="bp-side"><h2>Parts list</h2>
    <div class="bp-bomwrap"><table class="bp-bom">
      <thead><tr><th>Item</th><th>Part</th><th>Material / spec</th><th class="q">Qty</th></tr></thead>
      <tbody><tr data-part="1"><td><span class="n">1</span></td><td><b>Base</b></td><td class="m">Die-cast zinc</td><td class="q">1</td></tr>…</tbody>
    </table></div>
    <ul class="legend"><li><svg class="bp-key" viewBox="0 0 38 12"><path class="bp-outline" d="M1 6H37"/></svg>Outline</li>…</ul></div>
</div>
<div class="bp-extra">
  <h2>How to read it</h2><ol class="steps"><li class="c1"><b>Step title</b><span>One or two sentences.</span></li>…</ol>
  <h2>Good to know</h2><div class="cards"><div class="card c1"><svg><use href="#i-idea"/></svg><b>Title</b><p>…</p></div>…</div>
</div>
<p class="note">Simplified: … Sizes are illustrative …</p>
```
The sheet's paper, grid, border and zone letters/numbers are added by the page script — don't draw them. The player
(play / back / next, progress, caption) is built from `ol.steps` automatically, exactly as in /visualize.

### Parts, line weights and fills (classes only, no hard-coded colours)
| Need | Markup |
|---|---|
| A part (all its shapes in every view) | `<g class="bp-part" data-part="4" data-step="3"> … </g>` (several groups may share a number; `data-part="4 5"` lights both) |
| Visible edge (thick) | `class="bp-outline"` · thin detail edge `bp-detail` · very thin `bp-thin` |
| Hidden line (dashed) | `class="bp-hidden"` — toggled by the Hidden lines button |
| Centre line (dash-dot) | `class="bp-center"` · section / cut line `bp-cut` |
| Body fill (opaque tint, lights up on hover) | add `bp-body`: `<rect class="bp-outline bp-body" …/>`; translucent tint `bp-face`; solid wall / cut material `bp-solid`; erase what is behind `bp-paperfill` |
| Hatching for cut material | `<path class="bp-hatch" d="…"/>` (45°), `bp-hatch2` (−45°), `bp-hatchf` (fine), `bp-cross`, `bp-dots` (earth, concrete) |
| Hollow tube / cable | thick `bp-detail` (style stroke-width) + the same path with class `bp-hole` on top |
| Label text | `<text class="bp-t" x y>`; `bp-t sm`, `bp-t lg`, `bp-t cap` (caps), `bp-t dim`, `bp-t mute`, `bp-t halo` (paper outline) |

### Engine helpers (the page script draws these from data attributes; children are generated, so write them empty)
All coordinates are sheet units (0–1000, 0–700).

| Helper | Markup | Draws |
|---|---|---|
| Linear dimension (aligned) | `<g class="bp-dim" data-x1 data-y1 data-x2 data-y2 data-offset="22"></g>` | extension lines, dimension line, arrowheads, centred text; `data-offset` > 0 puts the line below a left-to-right dimension / left of a top-to-bottom one, < 0 the other side |
| Horizontal / vertical dimension | `<g class="bp-dim" data-type="h" data-x1 data-y1 data-x2 data-y2 data-at="420"></g>` (`v` likewise) | measures between feature points (their y may differ); the dimension line sits at `data-at` (y for h, x for v); extension lines start at each feature |
| Chain with ticks | add `data-end="tick"` | architectural slashes instead of arrowheads |
| Diameter / radius | `data-type="dia"` (or `rad`) `data-cx data-cy data-r data-angle="45" data-ext="24"` | leader through the circle, text outside, Ø or R added |
| Angle | `data-type="angle" data-cx data-cy data-r data-a1 data-a2` (degrees, screen angles, clockwise from +x) | arc with arrowheads and the angle text |
| Text | `data-text="130"` (optional) | if omitted, the text is **computed**: drawn length × the nearest ancestor's `data-k` (mm per unit) — preferred. A given `data-text` that disagrees with the drawing by > 4 % raises a WARN |
| Balloon | `<g class="bp-balloon" data-n="3" data-x data-y data-tx data-ty></g>` | numbered circle at (tx,ty), leader to the dot at (x,y) on the part; hover / focus links it to the parts-list row |
| View label | `<g class="bp-viewlabel" data-x data-y data-text="View A — Front" data-sub="Scale 1:3"></g>` | bold title with underline and a scale line (one per `g.bp-view`) |
| Title block | `<g class="bp-titleblock" data-title data-no data-scale data-units data-date data-by data-sheet="1 / 1"></g>` | bottom-right table (default 340 × 80); **required** |
| Notes box | `<g class="bp-notes" data-x data-y data-w="238" data-title="GENERAL NOTES" data-lines="a|b|c" data-valign="bottom"></g>` | boxed, numbered, auto-wrapped notes (`data-plain="1"` = no numbers); `data-y` is the top, or the bottom with `valign="bottom"` |
| Section line | `<g class="bp-section" data-x1 data-y1 data-x2 data-y2 data-label="A" data-dir="+"></g>` | cut line with end arrows and letters |
| Door (plan) | `<g class="bp-door" data-x data-y data-w data-angle="0" data-swing="+"></g>` | hinge point, door width, direction of the closed leaf (deg), swing + (clockwise) or − → leaf and swing arc |
| Window (plan) | `<g class="bp-window" data-x1 data-y1 data-x2 data-y2 data-t="8"></g>` | opening on the wall centre line with glazing lines (leave a gap in the wall drawing) |
| North arrow / scale bar | `<g class="bp-north" data-x data-y data-r="20"></g>` · `<g class="bp-scalebar" data-x data-y data-seg-px data-seg-val data-n="4" data-unit="m" data-title="SCALE 1:25"></g>` | symbol and a bar of `n` alternating segments |

A **view group** `<g class="bp-view" data-k="1.26">` says "1 sheet unit = 1.26 mm" for every dimension inside it. Dimension
the real feature points (so the numbers come out right), put the dimension lines outside the part, and keep ≥ 8 units between
parallel dimension lines. Don't hand-draw arrowheads.

### Interaction (automatic)
- Hover or focus a **balloon, a part in the drawing, or a parts-list row** → every element with the same `data-part` lights up
  (amber in Blueprint, orange in Whiteprint), the rest of the drawing dims. Works both ways, and with the keyboard.
- **Dimensions / Hidden lines / Grid** buttons show and hide a layer. **Print / Save PDF** opens the print dialog.
- **Walkthrough** (Play, ◀ ▶, or hover a step): lights every `[data-step]` group of that step, dims the rest, and lights the
  matching rows in the parts list. Keep each step's text self-contained.
- **Phones:** the sheet keeps an 860 px minimum width and scrolls inside its frame; the scroll hint says so.
- **Print:** Whiteprint, landscape, one page: the sheet with the title block on the left, the parts list beside it.

### Handwritten style (optional — OFF by default)
Leave `data-style` out. Add `data-style="handwritten"` on the stage (`<figure class="stage bp-stage" data-style="handwritten">`)
**only when the user asks** (handwritten, hand-drawn, pencil sketch, notebook style). Never choose it yourself, and keep it out
of default example markup. It turns the sheet into a **pencil sketch on graph paper**: cream paper with green graph grid, graphite
wobbly lines, handwriting fonts (Kalam / Caveat from Google Fonts; offline it falls back to a system handwriting font). There is
no theme button in this style (always paper) and it prints on white. Nothing else changes.

**Icons** (`#i-…`, used only in the "Good to know" cards): `sun cloud rain drop wave wind leaf sprout tree mountain fire thermo
bolt atom flask cell dna heart eye user users home factory bank truck globe flag laptop phone server db cpu code gear link lock
key shield search mail chat coin cart chart target idea doc book clock cal star check alert x loop`. Unknown names fail validation.

## Step 3 — Validate (when you have a code/computer tool)
Run it with the project's `.venv` Python if one exists (it has Playwright + Chromium); otherwise plain `python`:
```bash
# Windows
.venv\Scripts\python <skill-dir>/scripts/validate.py drawing.html --out <dir>
# macOS / Linux
.venv/bin/python <skill-dir>/scripts/validate.py drawing.html --out <dir>
```
It FAILS on leftover placeholders, external resources (Google Fonts only for the handwritten style), unknown icon ids, no
sheet or no title block, JavaScript errors, sideways page scroll, labels clipped by the border or overlapping each other, a
balloon, the title block or the notes box, overlapping balloons, a balloon number with no parts-list row (or a row with no
balloon), a dimension or balloon with missing data, hover that does not link balloon and row, layer buttons that do nothing,
and a print layout that is not light or still shows the controls. It WARNS on no scale, a view with no label, no dimensions or
balloons, a dimension text that disagrees with its drawn length, steps that do not match the `data-step` groups, more than one
printed A4 page, a portrait print, no scroll hint and hard-coded colours. It renders `*_light.png` (Whiteprint), `*_dark.png`
(Blueprint), `*_mobile.png` and `*_print.pdf`, and prints the printed page count. **Look at the PNGs in both themes** (and open
the PDF) and fix anything cramped, crossing, clipped, or hard to read: dimension lines through labels, balloons on top of
text, leaders crossing other leaders, empty or lopsided areas.

## Step 4 — Deliver
- Save as `examples/008-blueprint/<topic-slug>-blueprint.html` (unless the user or project names another place — never make a
  new top-level folder) and deliver it per the environment (publish as an artifact / present the file).
- If the user wants a PDF, tell them to use the **Print / Save PDF** button (or give the validator's `_print.pdf`).
- In chat, at most two lines: what the drawing shows (views, scale) and an offer (e.g. "want a section through the elbow, or
  it as a handwritten sketch?"). Don't repeat the page.

## Quality bar (self-check before delivering)
- **Realistic and consistent:** sizes are typical for the object and labelled illustrative unless from a real spec; dimensions
  come from the geometry; areas and totals add up; plan and elevation agree; part names are real.
- 2–4 labelled views with a stated scale, 8–12 numbered parts, every balloon in the parts list and every row on the sheet.
- Line weights clear (outline thick, detail thin, hidden dashed, centre dash-dot); dimensions outside the part, readable, none
  crossing text; title block and notes box complete; no overlaps.
- Hovering a balloon or a row lights the part; walkthrough steps match the reading guide; works in Blueprint, Whiteprint and on
  a phone; prints on one landscape page.
- The footnote names the simplifications and says the sizes are illustrative.
