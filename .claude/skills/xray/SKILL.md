---
name: xray
description: Reveal what is inside a body, animal, machine or system as a glowing radiograph-style page (cyan-and-white scanner tone, or a neutral white-and-grey film tone) — the outside as a faint translucent silhouette (or an attached photo turned into an x-ray), and the hidden inside drawn as bright labelled line-art (skeleton, organs, components) with the process inside animated (blood, current, data, nerve signals). A draggable x-ray scanner, a pointer lens and an Outside / X-ray / Both switch let the reader look through the shell; a numbered reading guide and a Play walkthrough move the scanner to each part. Monochrome cyan/white scan look by default (an optional multi-colour explainer look), a dark scanner screen with light page chrome in light mode, phone-friendly, prints with the inside shown, and an optional handwritten pencil-sketch style when asked. Use this whenever the user types /xray, or asks for an x-ray view, "see inside", "what's inside X", "show me inside X", a cutaway or see-through of a body part, organ, engine, phone, laptop, appliance, building wiring or plumbing, a tree trunk, "convert this image into an x-ray scan", "show the skeleton of a dog / hand / fish / bird", even if they don't say "x-ray". For parts pulled apart and numbered use /explodedview; for a general explainer scene use /visualize; for steps use /flowchart.
---

# /xray — see inside a body, machine or system

The output is ONE self-contained HTML page: an eyebrow, a headline with a colour accent, a one-line lede,
fact chips, **one x-ray stage** (the outside of the thing + its hidden inside, with a scanner), a legend, a
numbered reading guide with a Play walkthrough, 3 takeaways and a footnote. Light + dark, no external
assets (Google Fonts only in the optional handwritten style).

It must look like a **scan**, not a plain diagram: a deep navy-to-black screen, a faint cyan haze for the shell and soft tissue,
bright cyan-to-white glowing line-art for the inside (the brightest white for bones and dense parts), a faint scan grid and scan lines. And it must stay **true**: positions, parts and the
direction of every flow are correct for the real thing.

**Page theme:** pages open in the **Deep dark** theme (the scanner screen). A ☀/☾ button (built into the template, top right)
switches the page to the light theme and remembers the choice (the x-ray stage itself stays dark, because a radiograph is dark); the device's own dark mode is ignored.
Don't remove the button or add your own theme CSS. Check both themes (the validator renders both).
**Printing is always light** with the inside layer fully shown.

## Usage
`/xray <subject>` — e.g. `/xray a modern laptop showing the battery, CPU and motherboard`, `/xray a dog`, `/xray the human hand`.
`/xray` + an attached image — "convert the attached image into a high-contrast medical or technical X-ray scan; show the internal skeleton
and hidden internal components in glowing cyan/white tones against a deep dark-blue or black background" (see **Attached photo**).
Optional extras: audience (kid, student, engineer), depth, `colour` (explainer colours), `handwritten`, language.
Defaults: scan look, general audience, 6–13 labelled parts, 5–7 reading steps, English. With only `/xray` and no topic or image, ask for it in one short line.

## The two looks
- **`scan` (default; set nothing).** Monochrome radiograph: everything inside glows cyan to white on a deep navy-to-black screen with a soft bloom.
  `c1`–`c5` are *brightness levels*, not categories: `c4` = white (the brightest: bones, dense parts, the most important flow), `c3` = pale cyan,
  `c1` = cyan, `c2` = deeper blue, `c5` = dim steel (soft tissue, organs, shells). Say in the legend what each level means (e.g. "oxygen-poor blood (cyan)",
  "oxygen-rich blood (white)"). Use `bone` (below) for skeletons. Labels are cyan/white with a dark halo; badges are cyan; flows and particles are cyan/white.
- **Tone (inside the scan look): `cyan` or `film`.** `cyan` (default) is the scanner / tech style. `film` (`data-tone="film"` on the figure) is the neutral white-and-grey
  medical radiograph: bones pure white, soft tissue and shells a grey haze, no cyan anywhere, background near-black. **Use `film` for photo x-rays and medical-style requests**
  (it is the default when a photo is attached; add `data-tone="cyan"` to force cyan); use `cyan` for tech, gadgets and the scanner style. The user may ask for either.
- **`color` (the "explainer colours" option).** Add `data-look="color"` on the figure (`<figure class="stage xr-stage" data-look="color">`) **only when the user asks for colours** or when
  categories really matter (e.g. a wiring diagram with power / data / water in different colours). It keeps blue, green, amber, rose and violet with their meanings.
  Handwritten pages always use this look.

## Step 1 — Understand the thing
Write for yourself: *what is the hidden process, and where exactly does each part sit?* Pick a viewpoint
(front, side, cross-section) that shows the parts in their true places. Good topics: organs and bodies,
engines and machines, phones and laptops, a building's wiring/plumbing, a tree trunk, a washing machine.
- **Outside** = what you normally see (silhouette, face, casing), or the attached photo. Keep it simple: a shell, a few fine detail lines.
- **Inside** = the parts and the flow through them. Group by function or by the order things happen.
- **Accuracy is the whole value.** Anatomy and engineering facts, part positions, names, counts and the
  direction and order of flows must be correct. Mirror rules count (a front view of a body puts the patient's
  right on the left of the picture). Never invent numbers; approximate ones get "≈". Name every
  simplification in the footnote ("not to scale", "drawn side by side", "left out").

## Step 2 — Plan the content
- **Title** 2–5 words ("Inside the human heart"); headline = title with the key word in `<span class="accent">`; eyebrow `X-ray · <Anatomy|Machine|System>`; lede ≤ 25 words.
- **Chips** 2–4 real facts. **6–13 labelled parts** (each its own card). **5–7 steps** in the order things happen (a flow's order, or functions). One numbered badge per step on its lead card.
- **Colour = meaning**, max 4–5 families (`c1`–`c5`), explained by the legend (e.g. blue = oxygen-poor blood, red = oxygen-rich, amber = valves/power).
- **Motion**: only where something really travels (`.edge.flow` + `.particle`); a driver may `.pulse`.
- **3 takeaways**: the insight, a common mistake / gotcha (`i-alert`), a "so what".

## Step 3 — Build the page from the template
Copy `assets/template.html`. Replace `{{TITLE}}`, `{{HEADLINE}}`, `{{FORM}}`, `{{LEDE}}` and put the content where
`<!-- CONTENT GOES HERE -->` is. Don't rewrite the CSS, the `<defs>` or the scripts. The script builds the toolbar
(Outside / X-ray / Both, scanner slider, Lens), the draggable scanner and the Play bar by itself.

```html
<ul class="chips"><li><b>4</b> chambers</li>…</ul>
<figure class="stage xr-stage">
  <svg viewBox="0 0 960 680" data-scan="0.6" role="img" aria-label="one-sentence description">
    <rect class="xr-scan" x="…" y="…" width="…" height="…"/>      <!-- faint scan grid behind the object -->
    <g class="xr-outside"> <path class="xr-shell" d="…"/> <path class="xr-shell fine" d="…"/> </g>
    <g class="xr-inside">  …parts, back to front, each with data-step… </g>
    <g class="xr-labels">  …label cards with leader lines… </g>
  </svg>
  <figcaption>Drag the scanner … Point at a step below to highlight it.</figcaption>
</figure>
<p class="scroll-hint">← swipe the diagram →</p>
<ul class="legend">…</ul>
<h2>How to read it</h2> <ol class="steps"><li class="c1"><b>Title</b><span>1–2 sentences</span></li>…</ol>
<h2>Key takeaways</h2> <div class="cards">…</div>
<p class="note">Simplified: …</p>
```
Both layers share ONE coordinate space (viewBox width 960; height ≈ 600–700, with ≥ 30px free at the bottom
for the scanner handle). **Never put a `transform` on `.xr-outside`, `.xr-inside` or a parent of them** (the clip
uses the SVG's own coordinates). The scanner reveals the inside layer **left of the scanner line** (and inside the lens);
the outside layer is dimmed there. `data-scan="0.6"` sets where the scanner starts (0–1, default 0.5); `data-lens="80"` sets the lens radius.

### Components (inside `.xr-outside` / `.xr-inside`; classes only, no hard-coded colours)
| Need | Markup |
|---|---|
| Outer silhouette | `<path class="xr-shell" d="…"/>` (translucent, glowing edge); `xr-shell fine` = thin detail line; `xr-shell solid` = a button, notch |
| Faint outside detail | `<rect class="xr-app c1" …/>` (soft coloured shape) |
| Inside part (closed shape) | `<path class="xr-part c1" data-step="2" d="…"/>`; `bright` = stronger fill, `thin` = outline only, `dim` = background organ |
| Line art | `<path class="xr-line c2" data-step="3" d="…"/>` |
| Vessel / pipe / wire | `<g class="xr-tube c1" style="--w:24" data-step="1"><path d="D"/><path class="in" d="D"/></g>` (same `d` twice; `--w` = width) |
| Valve / gate / switch | `<path class="xr-valve c3" data-step="2" d="…"/>` (thick glowing stroke) |
| Bones / structure behind | `<path class="xr-bone" d="…"/>` / `xr-bone wide` |
| Flow inside a part | `<path id="f1" class="edge c1 flow" data-step="1" d="…" marker-end="url(#arr-c1)"/>` + `<circle class="particle c1" data-step="1" r="4.5"><animateMotion dur="3s" repeatCount="indefinite"><mpath href="#f1"/></animateMotion></circle>`; stagger extra dots with a **negative** `begin="-1.5s"` |
| Small tag text | `<text class="t small c1 halo" data-step="1" x y>from head</text>` |

**Part colours** `c1`–`c5` (scan look: brightness levels; colour look: blue, green, amber, rose, violet). **Draw order = z-order**: put each flow line right after the
part it runs in, and draw "behind" parts (e.g. a vessel that passes behind) before the parts that hide them.
**Every inside element carries its own `data-step="N"`** (steps are numbered 1…N as in the reading guide; shared parts `data-step="2 3"`).

### Skeletons and animals (a dog, a hand, a fish, a bird, a horse …)
Draw the **skeleton as the bright inner layer inside a faint body silhouette**, in a side view (or the view that shows the bones best), anatomically plausible and
correctly named. Build it back to front: body shell (outside layer) → soft organs (`xr-part c5 dim`, heart with `.pulse`) → ribs → vertebrae → skull and limb bones.
- Bones: `xr-part bone` (closed shapes: skull, pelvis, scapula, vertebra rectangles), `xr-tube bone round` (long bones: the tube markup with the same `d` twice; `--w` = width; pass an empty colour class), small circles for joints and wrist/ankle bones, `xr-bone` (white strokes: ribs, sternum). `bone` = the brightest white.
- Order and counts must be right. For a dog: skull, mandible, 7 cervical, 13 thoracic, 7 lumbar, 3 fused sacral and a variable number of tail vertebrae; 13 pairs of ribs; scapula, humerus, radius and ulna, carpals, metacarpals and phalanges in the front leg; pelvis, femur, patella, tibia and fibula, tarsals (the "hock" is the ankle, not the knee), metatarsals and phalanges in the hind leg.
- Sketch the key points first (in a Python script or on paper): body outline, spine curve, joint positions. Space vertebrae and ribs evenly along the curve. Keep limb proportions and joint angles true to the species.
- Keep cards to the **8–11 key bones** (skull, mandible, cervical vertebrae, scapula, humerus, radius and ulna, ribs, pelvis, femur, tibia and fibula …); use small `t small halo` tags for the rest ("thoracic vertebrae (13)", "tail vertebrae").
- Put cards left and right of the animal, and above or below it (the leader of a card on top starts at its bottom edge, of a card below at its top edge) so leader lines stay short. Motion: `.pulse` on the heart, and a dashed `.edge.flow` + `.particle` along the spinal cord (nerve signals).
- Say in the footnote that it is a generic, simplified illustration, not a real radiograph, and that counts vary between breeds.

### Attached photo (a whole-scene x-ray of the user's picture)
Use this when the user gives an image ("convert the attached image into an X-ray scan"). The result is a **photo scanner**: the original photo is the OUTSIDE layer, the
SAME photo filtered into a whole-scene x-ray is the INSIDE layer (with a drawn skeleton or components on top), and the scanner wipes between them like a real x-ray scanner over the scene.
**Be honest: this is NOT AI image generation.** The photo is only filtered to look like an x-ray (grayscale, inverted, dark tones, glowing edges, tone tint), and the skeleton / components are
a drawn illustration lined up with the photo by eye. Tell the user that in the delivery message, and say it in the footnote.
1. **Get the image next to the page.** Copy it beside the HTML file (relative path, e.g. `cat.jpg`; keep it small: crop to the subject and resize to ≈ 700–900 px wide, under ≈ 400 KB) or embed it as a `data:image/…;base64,` URI. No http(s) links (the validator fails them); a missing local file fails the validator.
2. **Look at the image** (open it with the file reader). Decide the crop, then the viewBox: width 960, height from the image's aspect ratio plus room for the cards (e.g. photo 880 × 590 at `x=40 y=110`, a row of cards above and below, `viewBox="0 0 960 830"`). The photo may fill the stage like a scene; cards sit in rows above and below it, or in side margins.
3. Markup (use the same `href` twice):
```html
<figure class="stage xr-stage" data-tone="film">                 <!-- film is already the default with a photo -->
  <svg viewBox="0 0 960 830" data-scan="0.5" data-photo-strength="1">
    <g class="xr-outside"><image class="xr-photo" href="cat.jpg" x="40" y="110" width="880" height="593" preserveAspectRatio="xMidYMid slice"/></g>
    <g class="xr-inside">
      <image class="xr-photo-xray" href="cat.jpg" x="40" y="110" width="880" height="593" preserveAspectRatio="xMidYMid slice"/>
      <g class="xr-bloomed"> …the drawn skeleton / components (bone parts, vertebrae, flows)… </g>
    </g>
    <g class="xr-labels"> …cards… </g>
  </svg>
```
   `.xr-photo` shows the picture unchanged (outside). `.xr-photo-xray` gets the template's filter (`#xr-photo-film` or, in the cyan tone, `#xr-photo-fx`): grayscale → invert → dark mid-tone curve → blurred edge glow screened on top → tone tint. `data-photo-strength="0.7"` on the svg fades the filtered photo. Wrap the drawing in `<g class="xr-bloomed">` (the glow is applied to the drawing only, not to the whole photo). Parts over a photo are slightly see-through, so the photo shows through the bones.
4. **Match the pose before drawing.** Look at the picture and write down (in a Python script or notes) the image coordinates of: the head (skull centre, nose, ear), the spine line (the neck, the highest point of the back, the rump, the tail base), the shoulder and hip, each visible leg joint (elbow, wrist, knee, hock) and paw, and the tail path. Convert them with one function `Q(x, y)` (crop origin and scale) so every part uses the same mapping. A curled or lying animal has an arched spine: sample the vertebrae along that curve (7 neck, 13 chest, 7 lower back, then the tail) and run the ribs inwards from the spine, not as a fan. Keep bone sizes in proportion to the head. Check the `_xray.png` against the photo, and fix anything that falls outside the animal.
5. If the pose is unclear or hidden by fur or blankets, say so, draw only what you can place with confidence, and keep the footnote honest ("positions are approximate"). Never claim the inside was "detected" from the photo.
6. **Credit the photo.** If the picture is not the user's own, add its author, licence and source URL in the footnote and a small Sources list. Use only public-domain / CC0 or licensed pictures.
7. Non-animal photos work the same way (a laptop, a car, a room): draw the internal components (battery, board, pipes …) over the photo, aligned with it.

### Label cards (inside `<g class="xr-labels">`)
Each main part gets a card with a leader line. Cards sit in the margins (left/right of the object), never over it.
```html
<g class="xr-label" data-focus-x="456">        <!-- appears once the scanner has passed x=456 (the part's right edge) -->
  <g data-step="2">
    <path class="leader" d="M256 146 L394 290"/><circle class="dot" cx="394" cy="290" r="3"/>   <!-- card edge → the part -->
    <g class="lift">
      <rect class="node c1" x="24" y="112" width="232" height="68" rx="16"/>
      <circle class="chip c1" cx="58" cy="146" r="20"/>
      <use href="#i-heart" class="ico on" x="46" y="134" width="24" height="24"/>
      <text class="t" x="88" y="142">Right atrium</text>
      <text class="t sub" x="88" y="163">receives blue blood</text>
    </g>
    <g class="badge c1" transform="translate(24,112)"><circle r="13"/><text text-anchor="middle" dy="4.5">2</text></g>  <!-- lead card of step 2 only -->
  </g>
</g>
```
Card width = 64 + longest line × 9px (title) or × 7.5px (sub) + 20; height 68. Order the cards top to bottom in the order
of their targets so leader lines don't cross. One badge per step (on the step's lead card). `data-focus-x` = the right edge
of the part (leave it off and the card shows whenever the inside is visible). **Icons** (`#i-…`): `sun cloud rain drop wave wind leaf sprout tree mountain fire thermo bolt atom flask cell dna heart eye user users home factory bank truck globe flag laptop phone server db cpu code gear link lock key shield search mail chat coin cart chart target idea doc book clock cal star check alert x loop`. Unknown names fail validation.

### What the page does by itself
- **Scanner**: a vertical line with a handle at the bottom; drag it, press ← → (Shift = bigger steps, Home/End), or use the slider. The inside layer shows left of it (SVG clipPath); the outside dims there (SVG mask); label cards fade in as the scanner passes their part.
- **Outside / X-ray / Both** switch (Both = scanner mode, the default), and a **Lens** toggle: a round window that follows the pointer (tap to place it on touch screens). Esc turns the lens off.
- **Play / reading guide**: highlights every `data-step` part and moves the scanner to the part's right edge. Hovering a step does the same.
- **Look**: the page's script sets `data-look` and `html.look-scan` (the CSS does the rest: bloom, dark stage, cyan ladder). Nothing to write for the scan look.
- **Phones**: the stage keeps a 640px minimum width and scrolls inside its card (a scroll hint shows); the toolbar and player stay in view. **Reduced motion**: flows and the scanner animation stop. **Print**: light colours, the inside layer fully shown, no controls.

### Handwritten style (optional — OFF by default)
Add `data-style="handwritten"` on the figure (`<figure class="stage xr-stage" data-style="handwritten">`) **only when the user
asks** (handwritten, notebook, pencil sketch). Never choose it on your own, and keep it out of default examples. It gives ruled
paper, handwriting fonts (Kalam / Caveat), a pencil-sketch look with no glow; the scanner works the same. It loads the two fonts from
Google Fonts (offline: a system handwriting font). These pages have no theme button (always paper).

## Step 4 — Validate (when you have a code/computer tool)
```bash
# Windows
.venv\Scripts\python <skill-dir>/scripts/validate.py page.html --out <dir>
# macOS / Linux
.venv/bin/python <skill-dir>/scripts/validate.py page.html --out <dir>
```
It FAILS on placeholders, external resources (Google Fonts only for handwritten), unknown icon/marker/path ids, JavaScript errors,
sideways scroll, clipped or overlapping labels and cards, a missing `.xr-outside` or `.xr-inside` layer, a scanner that does not
work (it moves it by code and by keyboard and checks that the clip and the labels change, plus the mode switch and the lens), and a print layout that is not light or still
clips the inside. It FAILS on an `<image>` that points at a missing local file or an http(s) URL (data: URIs and relative files are fine) and on a `data-look` value other than `scan` / `color` or a `data-tone` other than `cyan` / `film`. It WARNS on parts without labelled cards, steps without parts, badge/step mismatch, no motion, no scan grid or shell, hard-coded colours.
It renders `*_light.png`, `*_dark.png`, `*_mobile.png` and `*_xray.png` (dark, scanner fully revealing the inside).
**Look at all four PNGs** and fix anything wrong: parts in the wrong place, labels over parts, leader lines crossing text, shapes lost in one theme.

## Step 5 — Deliver
- Save as `examples/007-xray/<topic-slug>-xray.html` (unless the user or project names another place — never a new top-level folder) and deliver it per the environment.
- In chat, at most two lines: what the page shows and an offer (e.g. "want it handwritten, or zoomed into one part?").

## Quality bar
- 5-second test: the shell is clear, the scanner invites a drag, the inside parts glow and the flow is obvious.
- Every part is in its true place; every flow runs the true way in the true order; left/right are right for the viewpoint.
- Every main part has a card with a leader to the part; reading-guide numbers match the badges; Play lights up the right parts.
- Scan look: it truly looks like a glowing cyan/white radiograph (bones and dense parts brightest, shells a faint haze) and the legend explains the brightness levels; colour look: ≤ 5 colours with one meaning each. Works in light and dark and on a phone; nothing outside its card.
- Skeleton subjects: bones correctly named, counted, ordered and placed. Photo subjects: the original photo is the outside, the filtered whole-scene x-ray is the inside, the drawn inside lines up with the photo, and the credit and the "filtered photo + drawn illustration, not AI" note are in the footnote.
- Nothing invented; simplifications are named in the footnote.
