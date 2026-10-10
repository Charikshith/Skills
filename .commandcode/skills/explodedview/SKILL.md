---
name: explodedview
description: Break any physical object into its parts and show how they fit as a real 3D product viewer — a lifelike, drag-to-rotate exploded assembly (three.js, built from a small JSON spec) with studio lighting, PBR materials (chrome, anodised aluminium, glass, plastic, rubber, circuit boards), a floor shadow, numbered callout labels, a parts sidebar (hover, isolate, hide), an Explode slider, Assemble / Explode buttons, "Play assembly" with a step bar synced to the reading guide, x-ray mode, zoom / pan / reset / fullscreen / save-image tools, a parts list and keyboard shortcuts. Light and dark mode, phone-friendly, prints a still of the exploded view with the parts list, falls back to a still image without WebGL, and has an optional handwritten (toon + ink outline) style when asked. Use this whenever the user types /explodedview, or asks for an exploded view, exploded diagram, "break X into its parts", "show how X is put together / assembled", "what is inside X", a teardown, an assembly drawing or a parts breakdown of a physical object (pen, torch, phone, PC, engine, lamp, bicycle part), even if they don't say "exploded". For a process use /flowchart; for an idea map use /mindmap; for a general explainer visual use /visualize.
---

# /explodedview — an object → a 3D exploded product viewer

The output is ONE self-contained HTML page (about 700 KB; the three.js bundle is inlined, no network requests): an eyebrow, a
headline with a colour accent, a lede, chips, **a 3D viewer**, the **parts list**, the **assembly steps** (reading guide), 3
takeaways and a footnote. The agent writes **data, not geometry code**: a JSON spec describes every part as a few primitive
shapes with material presets; the page's engine builds the model, lights it like a studio and gives it a professional viewer UI.

It must look like a **manufacturer's product-viewer render** and stay **true**: real proportions, correct part names, correct
assembly order, nothing invented. The models are illustrative (primitives, not CAD) and the footnote says so.

**Page theme:** pages open in the **Deep dark** theme (a dark studio). A ☀/☾ button (built into the template, top right)
switches to the light studio and remembers the choice; the device's own dark mode is ignored. The 3D scene repaints live.
Don't remove the button or add your own theme CSS. Check both themes (the validator renders both).
**Printing is always light**: a still image of the EXPLODED view plus the parts list; controls and sidebar are hidden.

## Usage
`/explodedview <object>` — optional extras: level ("simple", "detailed"), version or size ("147 mm phone"), audience,
`handwritten`, language. Defaults: the common version of the object, 6–10 parts, English.
If the user gives only `/explodedview` with no object, ask for the object in one short line.

## Step 1 — Understand the object
- **Which version?** "A click pen", "a Maglite-style torch with 2 AA cells", "a smartphone". Say it in a chip and the footnote.
- **Real size.** Recall or look up the real dimensions (a click pen ≈ 140 mm long, 10 mm wide, refill ≈ 105 mm, spring ≈ 15 mm;
  a phone ≈ 147 × 71.5 × 8 mm) and build in ONE unit (mm). State the reference size in the spec `size` (shown in the viewer) and
  in a chip. Never draw a tiny cone with a giant refill.
- **One explode axis.** Parts are pulled apart along ONE straight line, the way they are assembled: along the object's length
  (pen, torch) or straight up its thickness (phone, PC case, lamp). Put every part on that line in assembly order. Only small
  side parts (a clip, a button, a screw) may step a short distance off the axis. Parts that slide *into* another part are pulled
  out along the axis past its end.
- **List 6–10 parts** (hard cap ~14; group screws and washers into one row). Order = assembly order (what you would do first … last).
  Check each name and the order against how the thing is really built. If unsure of a detail, leave it out or say so in the footnote.
- **Parts that hide each other.** The default camera looks from the front-right and slightly above. Opaque layers above a part hide
  its far end; make the gap between layers big enough (≳ 40 mm for a 147 mm phone at 20° elevation) or make the upper layer glass.
  Give every part a `label` point that is visible in the default view.

## Step 2 — Plan the page
- **Title** 2–5 words; headline = the title with a key word in `<span class="accent">`; eyebrow `Exploded view · <Everyday object|Technology|…>`; lede ≤ 25 words.
- **Chips** (3–4): number of parts, steps, the version, the real size.
- Numbers = assembly order (`n` = `order` = 1…N) so labels, list and steps agree.
- **Colour = kind of thing** (`tone` `c0`–`c5`, max 4 families) for the labels, rows and step bar: e.g. metal `c0`, plastic body `c1`, electronics `c2`, power `c3`, ink `c4`, mechanism `c5`.
- **3 takeaways** with icons: how it works (`i-idea`), a mistake or safety point (`i-alert`), a "so what" (`i-target`). **Footnote:** simplifications, "not CAD".

## Step 3 — Build the page from the template
Copy `assets/template.html`. Replace `{{TITLE}}`, `{{HEADLINE}}`, `{{FORM}}`, `{{LEDE}}` and put the content where
`<!-- CONTENT GOES HERE -->` is. Don't edit the CSS or the scripts. **Content skeleton:**
```html
<ul class="chips"><li><b>8</b> parts</li><li>About <b>140 mm</b> long</li></ul>
<figure class="ev3d" id="ev3d">
  <figcaption>What the reader is looking at. Drag to rotate, scroll to zoom, or press Play assembly.</figcaption>
</figure>
<h2>Parts list</h2><div id="ev-partslist"></div>            <!-- the engine writes the table from the spec -->
<h2>How it goes together</h2><ol class="steps" id="ev-steps"></ol>   <!-- ... and the reading guide -->
<h2>Key takeaways</h2><div class="cards"><div class="card c1"><svg><use href="#i-idea"/></svg><b>Insight</b><p>…</p></div>…</div>
<p class="note">Simplified: an illustrative model built from simple shapes, not CAD. …</p>
<script type="application/json" id="ev-spec">{ …the spec… }</script>
```
The engine builds the viewer inside the `<figure>` (sidebar, canvas, callouts, toolbar, controls, step bar), writes the parts
table and the steps list, and wires everything. Don't write balloons, tables or step lists by hand.

### The spec (`#ev-spec`)
Coordinates: **x right, y up, z toward the viewer**, in the spec's unit (use mm). Angles in degrees.
```json
{ "title":"Inside a ballpoint pen", "units":"mm", "slug":"pen-exploded", "size":"about 140 mm long, 10 mm wide",
  "view":{"az":28,"el":22}, "aspect":2.1, "aspectMobile":1.5,
  "parts":[ { "n":1, "name":"Nose cone", "qty":1, "role":"Chrome-plated metal. The tapered front …", "order":1, "tone":"c0",
              "material":"chrome", "at":[0,0,0], "explode":[0,0,0], "label":[x,y,z], "step":"Hold the nose cone point down …",
              "shapes":[ {"type":"lathe","axis":"x","profile":[[1,0],[4.9,18]]}, … ] }, … ] }
```
| Key | Meaning |
|---|---|
| `view` | default camera direction: `az` (0 = from +z, positive towards +x), `el` (above the floor) |
| `aspect`, `aspectMobile` | stage width / height (default 1.6 on desktop, about 1 on phones); use ~2 for long thin objects |
| part `n`, `order` | number and assembly order (parts with the same order arrive together) |
| part `at` | where the part sits ASSEMBLED (offset of its origin); shapes are positioned relative to it |
| part `explode` | how far it moves at 100 % exploded `[dx,dy,dz]` (same axis for every part; 0 for the base part) |
| part `material` | default material for its shapes (a preset name or `{preset, color, roughness, …}`) |
| part `label` | optional anchor `[x,y,z]` for the callout (default: the top corner nearest the camera) |
| part `role`, `step` | one-line material / role (parts list, tooltip); the sentence for the step |
| part `tone` | colour family `c0`–`c5` for its label, list row and step bar |

### Shapes (every shape: `type`, optional `pos`, `rot`, `material`, `edges`, `repeat`)
Round shapes take `"axis":"x"|"y"|"z"` (default y) and `"span":[t0,t1]` (absolute start and end along that axis; or `h` + `pos`).
| `type` | Parameters | Makes |
|---|---|---|
| `box`, `rbox` | `size:[w,h,d]`, `radius` (rbox) | box, rounded box (buttons, chips, batteries) |
| `cyl`, `cone` | `r`, `r2` (other end; 0 = cone), `span`, `segments`, `open` | cylinder, frustum, cone |
| `tube` | `rOut`, `rIn`, `span` | hollow cylinder (rings, barrels, lens rims) |
| `lathe` | `profile:[[r,t],…]` (radius, position along the axis) | turned part: barrels, nose cones, buttons, bottles; close the profile (end where you started) for a hollow shell |
| `extrude` | `plane:"xz"` (flat, extrudes up; default) or `"xy"`; `rect:[w,d]`+`radius`, `circle:r` or `outline:[[u,v],…]`; `at:[u,v]`; `holes:[…same…]`; `depth`; `bevel` | boards, frames (with a hole), glass panes, clips, brackets |
| `coil` | `r`, `wire`, `turns`, `span` | spring |
| `thread` | `r`, `pitch`, `depth`, `span` | threaded section (a helical ridge on a core) |
| `torus`, `sphere` | `R`,`r` / `r`,`scale:[sx,sy,sz]` | ring, ball |
| `label` | `size:[w,d]`, `pos`, `rot`, `text:[lines]`, `bg`, `color`, `fontSize`, `radius`, `preset:"traces"/"logo"/"coil"/"bezel"` | printed decal lying on a face (battery label, chip marking, PCB traces, black screen bezel) |
| `screen` | `size`, `pos`, `radius`, `clock`, `date`, `wallpaper:[c1,c2,c3]`, `apps` | lit phone screen (wallpaper, clock, icons) |
`repeat:{"count":6,"axis":"x"}` rotates copies around an axis (teeth, bolts). `edges:"#ffffff"` adds thin edge lines (glass panes).
Holes and openings: use `extrude` with `holes`, or overlay a thin dark `rbox`.

### Materials (a preset name, or `{"preset":"plastic_gloss","color":"#2f58c9"}`; unknown presets fail validation)
`aluminium` `anodised` `steel` `chrome` `brass` `copper` `gold` · `glass` (clear, reflective), `glass_back` (frosted coloured) ·
`plastic_gloss` `plastic_matte` `rubber` `ceramic` `black_gloss` `display` · `pcb_black` `pcb_green` `battery_foil` ·
`ink` `clear_plastic` `led` `lens_glass`. Overrides: `color`, `metalness`, `roughness`, `opacity`, `emissive`, …
Build every part from several shapes (body + details: grooves, threads, chips, buttons, ports) so it reads as a real part.

## What the viewer does by itself
- **Rotate** (drag / one finger), **zoom** (wheel / pinch / + −), **pan** (right-drag / two fingers / shift-drag), **Reset view**, **Auto-rotate**,
  **Labels** on/off, **X-ray**, **Fullscreen**, **Save image** (PNG). The view auto-fits the model (assembled = big, exploded = everything fits) until the user zooms or pans.
- **Explode slider**, **Assemble**, **Explode**, **Play assembly** (parts fly in one by one in `order`, the camera follows), **step bar** "Step 3 / 7" with prev / next and one segment per step, synced with the reading guide (click a card to jump to that step).
- **Parts sidebar** (a bottom list on phones): hover highlights the part in 3D, click isolates it (others ghosted) and again restores, the eye hides / shows, "Show all". **Callout labels** are HTML, follow the parts, avoid each other and dim when their part is hidden behind another.
- Hover a part: tooltip with name and role; the sidebar row, label and parts-list row light up. Click a part: isolate.
- **Keyboard** (focus the viewer): arrows orbit, + / − zoom, R reset, E explode / assemble, Space play / pause, L labels, X x-ray, F fullscreen. **Reduced motion:** no auto-rotate, instant moves.
- **No WebGL:** the embedded still image (or a message) plus the parts list and steps. **Print:** light, a still of the exploded view, the parts list.

### Handwritten style (optional — OFF by default)
Leave `data-style` out. Add `data-style="handwritten"` on the figure (`<figure class="ev3d" data-style="handwritten">`) **only when the user asks**
(handwritten, notebook style). Never choose it yourself. It gives toon shading with ink outlines on ruled paper and handwriting fonts
(Google Fonts; offline a system font); the page has no theme button.

**Icons** (`#i-…` in takeaway cards): `sun cloud rain drop wave wind leaf sprout tree mountain fire thermo bolt atom flask cell dna heart eye user users home
factory bank truck globe flag laptop phone server db cpu code gear link lock key shield search mail chat coin cart chart target idea doc book clock cal star
check alert x loop`.

## Step 4 — Validate (needs Python with Playwright + Chromium, and WebGL; headless Chromium's software WebGL works)
```bash
# Windows
.venv\Scripts\python <skill-dir>/scripts/validate.py page.html --out <dir> --embed-poster
# macOS / Linux
.venv/bin/python <skill-dir>/scripts/validate.py page.html --out <dir> --embed-poster
```
It FAILS on placeholders, external resources (the three.js bundle must stay inline), raster images other than the embedded poster,
a spec that is not valid JSON, unknown shape types or materials, duplicate part numbers, JavaScript errors, sideways page scroll,
a blank canvas, **parts overlapping each other when exploded (3D boxes)**, parts that are not at `at` when assembled or at
`at + explode` when exploded, an assembled model filling < 50 % (exploded < 40 %) of the stage width, callout labels off screen
or overlapping, a missing parts-list row / sidebar row / label for a part, broken controls (zoom, reset, isolate, hide, show all,
x-ray, labels, every step, save image), a missing no-WebGL fallback, and a print layout that is not a light still of the exploded view
with the parts list. It WARNS on more than 14 parts, order gaps, parts that never move, a label hidden in the default view, and a
file over 2.5 MB. `--embed-poster` stores a still of the exploded view inside the page for browsers without WebGL.
It renders `*_light.png`, `*_dark.png`, `*_mobile.png`, `*_assembled.png`, `*_exploded.png` and `*_print.pdf`.
**Look at the PNGs**: materials must read correctly (metal vs plastic vs glass), nothing tiny in empty space, labels not
covering the model, parts separated cleanly along one axis, both themes readable, the phone layout clean. Fix and re-run.
If you can't run a browser, still write the spec carefully and say that it was not validated.

## Step 5 — Deliver
- Save as `examples/009-explodedview/<object-slug>-explodedview.html` (unless the user names another place; never make a new top-level folder).
- If the user wants an image: the `_exploded.png` / `_assembled.png`, or the viewer's **Save image** button.
- In chat, at most two lines: what the model shows and an offer ("want a different camera angle, or the torch next?").

## Honest notes
Models are illustrative, built from primitives, not CAD: say it in the footnote together with the main simplifications (parts left
out, thickness exaggeration, orientation tricks such as camera lenses facing up). three.js (MIT licence) is bundled in the page; its
licence text is in a comment at the top of the page and in `assets/vendor/LICENSE-three.txt`.

## Quality bar (self-check before delivering)
- **Would this pass as a product-viewer render on a manufacturer's website?** Real proportions with a stated size, believable
  materials (chrome vs gloss plastic vs frosted glass vs PCB), detail on every part, soft shadow, sensible lighting in both themes.
- **Part names, count and assembly order are correct** for the stated version; number = order everywhere.
- One explode axis, parts separated cleanly, every label visible in the default view, assembled = one believable object.
- ≤ 4 colour families; controls work on desktop and phone; the fallback and print still exist.
- Nothing invented: simplifications are named in the footnote.
