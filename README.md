# Visual skills for coding agents

Real, tested versions of slash commands from the "100 Powerful ChatGPT AI Commands" list.
Each skill makes **one self-contained HTML page**. Each one has a template, so the look stays
the same every time, and a validator that checks the page and takes screenshots.

Works with **Claude Code, OpenAI Codex, Pi and Command Code**. All four use the open
[Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`).

## The skills

| # | Skill | What it makes | Try |
|---|---|---|---|
| 1 | `visualize` | An illustrated explainer: one SVG scene or diagram (flow, cycle, layers, anatomy …) with icons, motion on what moves, hover-to-highlight and a Play walkthrough | `/visualize how DNS works` |
| 2 | `handwritten` | A notebook-style study page: ruled paper, pen and highlighter, a hand-drawn diagram, a sticky-note tip | `/handwritten photosynthesis with diagrams` |
| 3 | `infographic` | A poster of real numbers: a giant hero stat, count-up tiles, icon rows ("7 in 10"), bars, donuts, A-vs-B. **Every number has a year and a source** | `/infographic water on Earth` |
| 4 | `diagram` | A box-and-arrow structure diagram (architecture, network, pipeline, parts of a cell) with shapes per kind and group boxes, laid out automatically. "Try a flow" buttons | `/diagram how a web app is built` |
| 5 | `flowchart` | A real flowchart: start/end, steps, Yes/No decisions, loops, optional swimlanes, laid out automatically. "Try a path" buttons | `/flowchart paying by card online` |
| 6 | `mindmap` | A mind map: a centre and 5–7 colour-coded curved branches, laid out automatically. Click a branch to fold it | `/mindmap how the internet works` |
| 7 | `xray` | An x-ray scan: the outside as a faint shape (or **your photo turned into an x-ray**) and the inside (skeleton, organs, parts) glowing in cyan or white film tones. Drag a scanner to look inside | `/xray a dog` |
| 8 | `blueprint` | A technical drawing: front / side / top views or a floor plan, real dimension lines, numbered parts, a title block. Blueprint (dark) or Whiteprint (light) | `/blueprint a desk lamp` |
| 9 | `explodedview` | A **3D product viewer**: an object pulled apart into lifelike parts (metal, glass, plastic, circuit boards) with studio lighting. Drag to rotate, zoom, isolate a part, x-ray mode, an explode slider and "Play assembly" | `/explodedview inside a ballpoint pen` |
| 10 | `thenvsnow` | Past vs present: a before/after slider, numbers with the % change worked out, and sources for every figure | `/thenvsnow computers 1984 vs today` |
| 11 | `timeline` | A time axis with event cards joined to their exact dates, coloured eras, optional lanes, laid out automatically | `/timeline the history of the internet` |
| 59 | `cheatsheet` | A dense quick-reference page: colour-grouped sections, copyable code, formulas, gotchas, live search. Prints on 1–2 pages | `/cheatsheet Git essentials` |

Every skill has light and dark mode, works on a phone, and has an optional
**handwritten notebook style** (ruled paper, pen lines, sticky notes) — add `handwritten` to the request.
It is only used when you ask for it.

Also installed in this repo: `lavish`, a third-party skill (by Kun Chen, MIT) that opens an HTML page
in your browser so you can mark it up and send feedback to the agent. It came from
`npx skills add kunchenguid/lavish-axi --skill lavish` and is tracked in `skills-lock.json`.

### Examples
Every example page is in `examples/<NNN>-<skill>/`. NNN is the command's number in the PDF list.
New pages are saved there too.

| Folder | Pages |
|---|---|
| `001-visualize/` | `dns-resolution-visual.html`, `water-cycle-visual.html`, `new-forms-preview.html` |
| `002-handwritten/` | `photosynthesis.html` |
| `003-infographic/` | `water-on-earth-infographic.html`, `solar-system-in-numbers-infographic.html` (handwritten) |
| `004-diagram/` | `web-app-architecture-diagram.html`, `animal-cell-diagram.html` (handwritten) |
| `005-flowchart/` | `card-payment-flowchart.html`, `quadratic-equation-flowchart.html` (handwritten) |
| `006-mindmap/` | `how-the-internet-works-mindmap.html`, `photosynthesis-mindmap.html` (handwritten) |
| `007-xray/` | `inside-the-human-heart-xray.html`, `inside-a-smartphone-xray.html`, `a-dog-xray.html`, `cat-photo-xray.html` (photo: `cat-curled-on-sofa.jpg`, CC0 by Sonkiki, Wikimedia Commons) |
| `008-blueprint/` | `desk-lamp-blueprint.html`, `tiny-house-floor-plan-blueprint.html` |
| `009-explodedview/` | `ballpoint-pen-explodedview.html`, `smartphone-layers-explodedview.html` |
| `010-thenvsnow/` | `computers-1984-vs-2025-thenvsnow.html`, `world-population-and-life-expectancy-1950-vs-2023-thenvsnow.html` |
| `011-timeline/` | `history-of-the-internet-timeline.html`, `world-war-2-timeline.html` (handwritten) |
| `059-cheatsheet/` | `git-essentials-cheatsheet.html`, `trigonometry-formulas-cheatsheet.html` (handwritten) |

---

## Prerequisites

**To use a skill, you need only:**
- one of the 4 agents (Claude Code, Codex, Pi or Command Code), and
- a modern web browser (Chrome, Edge, Firefox or Safari) to open the page it makes.

No API keys, no accounts, no packages. The pages are plain HTML files.

**Extra things, only when you need them:**

| You want to … | You need | Which skills |
|---|---|---|
| Install with `install.py` | Python 3.8 or newer (no packages) | all |
| Let the agent check its page and take screenshots (recommended) | Python 3.8+, plus Playwright and Chromium in `.venv` (see Install, step 3) | all except `lavish` |
| Use the handwriting fonts | Internet when you open the page (Google Fonts). Offline, a plainer handwriting font is used | `handwritten` always; the others only in the handwritten style |
| Use `lavish` | Node.js (it runs `npx lavish-axi`) | `lavish` only |
| Install with `npx skills add` | Node.js | any (if this repo is on GitHub) |
| Turn your own photo into an x-ray | The photo file (JPG or PNG) | `xray` only |
| See the 3D view | A browser with WebGL (all modern browsers). Without it, a still picture and the parts list are shown. Each page is about 0.7 MB because the 3D engine (three.js, MIT) is inside it | `explodedview` only |

---

## What is in this repo

```
.agents/skills/<skill>/          <- MAIN COPY (Codex + Pi read this folder)
  SKILL.md                       <- instructions the agent follows
  assets/template.html           <- page template (CSS, icons, scripts)
  scripts/validate.py            <- checks the page + renders screenshots
.claude/skills/<skill>/          <- copy for Claude Code
.commandcode/skills/<skill>/     <- copy for Command Code
examples/<NNN>-<skill>/          <- example pages per skill
install.py                       <- copies skills to agent folders
requirements.txt                 <- Python package for the validators (Playwright)
skills-lock.json                 <- records where the third-party lavish skill came from
handwritten.skill                <- original zip of the handwritten skill
```

| Agent        | Project folder          | User (all projects) folder |
|--------------|-------------------------|----------------------------|
| Codex        | `.agents/skills/`       | `~/.agents/skills/`        |
| Pi           | `.agents/skills/`       | `~/.pi/agent/skills/`      |
| Claude Code  | `.claude/skills/`       | `~/.claude/skills/`        |
| Command Code | `.commandcode/skills/`  | `~/.commandcode/skills/`   |

> **Edit only `.agents/skills/<skill>/`.** Then run `python install.py` to copy the
> change to the other folders. The copies are real files, not symlinks, so it works on
> Windows without admin rights.

---

## Install

### 1. Get the files
Clone or download this repo.

### 2. Put the skills where your agent looks

```bash
python install.py --list                                # see the skill names
python install.py                                       # all skills, into this repo
python install.py --target /path/to/your-project        # all skills, into another project
python install.py --target /path/to/your-project --skills flowchart          # only 1 skill
python install.py --target /path/to/your-project --skills flowchart,mindmap  # a few skills
python install.py --target /path/to/your-project --agents claude,codex       # only some agents
python install.py --global --skills flowchart           # for your user (every project)
```
Agent names: `codex`, `pi`, `claude`, `commandcode`. A wrong skill name gives an error and
tells you to run `--list`.

### 3. Set up Python for the validators (optional, recommended)
The validators use Playwright and Chromium to check the page and take screenshots.
Run these commands in the project root:

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
```

macOS / Linux:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

With [uv](https://docs.astral.sh/uv/):
```bash
uv venv .venv
uv pip install --python .venv -r requirements.txt
.venv/bin/python -m playwright install chromium   # Windows: .venv\Scripts\python
```

The skills tell the agent to use `.venv`'s Python when it exists. Without it the skills still
make the page; they just skip the automatic check.

### 4. Restart your agent
Most agents scan for skills only when they start.

---

## Use it

| Agent        | How to call a skill                     | Example |
|--------------|-----------------------------------------|---------|
| Claude Code  | `/<skill> <topic>`                      | `/flowchart paying by card online` |
| Codex        | `$<skill> <topic>` (or pick from `/skills`) | `$flowchart paying by card online` |
| Pi           | `/skill:<skill> <topic>`                | `/skill:flowchart paying by card online` |
| Command Code | `/<skill> <topic>`                      | `/flowchart paying by card online` |

You can also just ask in plain words, for example "make a flowchart of …".
The output is one `.html` file. Open it in a browser.

### Page theme
Pages open in a **dark theme**. Click the **☀** button at the top right to switch to light,
and **☾** to go back. The page remembers your choice. It does not follow your computer's dark mode.
Handwritten-style pages always look like paper and have no button. `/blueprint` calls its two
themes Blueprint (dark) and Whiteprint (light). The `/xray` scan screen stays dark in both.

### Options for each skill

#### `/visualize` (#1)
Audience (`for a kid`, `for engineers`), form (`as a cycle`, `as layers`, `as a timeline` …), depth (`simple`, `detailed`).
```
/visualize how a bill becomes law in India
/visualize the water cycle, for a 10-year-old
/visualize Kubernetes architecture as layers, for engineers
```
If you name no form, the skill picks the best one.

#### `/handwritten` (#2)
Level (`class 10`, `undergrad`, `interview prep`), length (`1 page`, `detailed`), `with diagrams`.
```
/handwritten Newton's laws of motion, class 9
/handwritten TCP vs UDP, interview prep, detailed
```

#### `/infographic` (#3)
Your own data, audience, region or years, `handwritten`.
```
/infographic water on Earth
/infographic our sales numbers: Q1 12.4M, Q2 13.1M, Q3 15.0M
/infographic the solar system in numbers, handwritten
```
**Sources are always listed.** Only real numbers are used, each with its year. If a number cannot
be checked, it is left out. Your own numbers are used exactly as you wrote them.

#### `/diagram` (#4)
Direction (`top to bottom`), depth (`simple`, `detailed`), `handwritten`.
```
/diagram how a web app is built: browser, CDN, servers, database, queue
/diagram AWS three-tier architecture with a VPC and public and private subnets
/diagram parts of an animal cell and how they work together, handwritten
```
Hover a box to see what it connects to, click a group to focus on it, and use **Try a flow**
to watch a request travel through it.

#### `/flowchart` (#5)
`with swimlanes` (who does what), depth, `handwritten`.
```
/flowchart paying by card online
/flowchart employee leave request, with swimlanes
/flowchart my laptop won't turn on — troubleshooting
/flowchart solving a quadratic equation, handwritten
```
Use **Try a path** to watch one scenario travel through the chart.

#### `/mindmap` (#6)
Depth, audience, `handwritten`.
```
/mindmap how the internet works
/mindmap climate change: causes, effects, solutions
/mindmap photosynthesis, handwritten
```
Click a main branch to fold it, hover to follow a branch.

#### `/xray` (#7)
`film` (white/grey medical look instead of cyan), `colour` (colour-coded explainer look), `handwritten`, or attach a photo.
```
/xray the human heart
/xray a dog
/xray a modern laptop showing the battery, CPU and motherboard
/xray  (attach a photo)  turn this into an x-ray scan showing the skeleton
```
Drag the **scanner**, or press the arrow keys, to look through the outside. **Outside / X-ray / Both**
switches the view, and **Lens** gives a round window that follows your pointer.
With a photo: the scanner wipes from your colour photo to an x-ray of the whole scene, with a
skeleton or parts drawn on top. **This is not AI image generation** — the photo is filtered and the
inside is a drawing, lined up with your photo.

#### `/blueprint` (#8)
Views (`plan and elevation`, `front and side`), scale (`1:20`), `simple` / `detailed`, `handwritten` (pencil on graph paper).
```
/blueprint a desk lamp
/blueprint road bicycle frame, front and side views
/blueprint tiny house floor plan, 6 m by 2.5 m, 1:25
```
**Dimensions**, **Hidden lines** and **Grid** buttons show or hide those layers. **Print / Save PDF**
prints one landscape page. Sizes are illustrative unless you give a real spec.

#### `/explodedview` (#9)
View (`isometric`, `side view`), `simple` / `detailed`, `handwritten`.
```
/explodedview inside a ballpoint pen
/explodedview smartphone layers
/explodedview a torch with two AA batteries, side view
```
It is a real 3D viewer:
- **Drag** to rotate, **scroll / pinch** to zoom, **right-drag** to pan. Toolbar: zoom, reset, auto-turn, labels, x-ray, fullscreen and save as PNG.
- **Parts list** on the side: hover to highlight, click to isolate a part, the eye icon hides it.
- The **Explode** slider, **Assemble** / **Explode** buttons, and **Play assembly**, which flies the parts in one by one with a "Step 3 / 7" bar.
- Keys: arrows rotate, `+` / `−` zoom, `R` reset, `E` explode, `Space` play, `L` labels, `X` x-ray, `F` fullscreen.

The models are built from simple 3D shapes, drawn to scale. They are illustrations, not CAD files.

#### `/thenvsnow` (#10)
The topic and two years, or your own numbers, `handwritten`.
```
/thenvsnow computers 1984 vs today
/thenvsnow the world in 1950 vs 2023
/thenvsnow our sales in 2019 and 2025: 120 and 310 orders
```
Every figure is listed under **Sources**. The % change is worked out for you.

#### `/timeline` (#11)
A date range, `with lanes` (parallel tracks), depth, `handwritten`.
```
/timeline the history of the internet
/timeline space exploration, 1957 to 1975
/timeline World War II key events, handwritten
```
When the dates are very uneven, the events are spaced evenly and the time jump is marked.

#### `/cheatsheet` (#59)
Level (`beginner`, `class 10`, `interview`), a version (`Python 3.12`), size (`1 page`), `handwritten`.
```
/cheatsheet Git essentials
/cheatsheet Python 3.12 basics, beginner
/cheatsheet trigonometry formulas for class 10 to 12, handwritten
```
Type in the **search box** (or press `/`), **★ Most used** shows the key rows, each code snippet has
a **Copy** button, and **Print / Save PDF** prints a light page on 1–2 sheets.

---

## Check a page by hand

Every skill has a validator in `.agents/skills/<skill>/scripts/validate.py`:

```bash
# Windows
.venv\Scripts\python .agents\skills\<skill>\scripts\validate.py examples\<NNN>-<skill>\<page>.html --out out
# macOS / Linux
.venv/bin/python .agents/skills/<skill>/scripts/validate.py examples/<NNN>-<skill>/<page>.html --out out
```
`RESULT: PASS` means the page is OK. The screenshots go to the `--out` folder.

| Skill | Main checks (FAIL) | Screenshots |
|---|---|---|
| all | placeholders left in the page, files loaded from the internet, unknown icons, JavaScript errors, sideways scroll, text clipped or overlapping | — |
| visualize | badge count = step count | light, dark, mobile |
| handwritten | — (warns if the web font is not loaded) | desktop, mobile |
| infographic | Sources list missing, a source link pointing nowhere, a count-up ending on the wrong number, bad chart data | light, dark, mobile, print PDF |
| diagram | boxes overlapping, a box outside its group, groups overlapping, labels on boxes | light, dark, mobile |
| flowchart | bad spec, shapes overlapping, labels on shapes | light, dark, mobile |
| mindmap | bad spec, labels or shapes overlapping, text spilling out of a pill | light, dark, mobile |
| xray | missing outside or inside layer, scanner, switch or lens not working, missing photo file | light, dark, mobile, x-ray |
| blueprint | missing title block, a balloon without a parts-list row, a dimension with missing data | light, dark, mobile, print PDF |
| explodedview | parts overlapping when exploded, parts not back in place at 0%, a balloon without a parts row | light, dark, mobile, assembled, exploded, print PDF |
| thenvsnow | a written % that does not match the numbers, figures without Sources, a slider that does not move | light, dark, mobile, print PDF |
| timeline | dates that cannot be read, cards overlapping, lines through cards | light, dark, mobile |
| cheatsheet | broken search, text spilling out of a section, a print that is not light | light, dark, mobile, print PDF |

Each validator also gives WARN lines for softer problems, such as too many items or a missing year.
For the handwritten style, a `web font not loaded` WARN only means that you are offline.

---

## Add the next command from the list
1. Copy the closest skill, for example `.agents/skills/visualize/`, to `.agents/skills/<new-name>/`.
2. Change the `name` and `description` in `SKILL.md`, then change the steps.
3. Save its examples in `examples/<NNN>-<new-name>/`.
4. Run `python install.py` and restart your agent.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| The agent does not see the skill | Restart the agent. Make sure that the folder for that agent (table above) contains `<skill>/SKILL.md`. |
| `No module named 'playwright'` | Do Install step 3, then run the validator with `.venv`'s Python. |
| `Executable doesn't exist … chromium` | Run `<venv-python> -m playwright install chromium`. |
| `unknown skill(s)` from `install.py` | Run `python install.py --list` and copy the exact name. |
| Pi warns of a name collision | Pi found the skill in two places (for example `~/.agents/skills` and the project). Remove one. |
| I edited a skill but nothing changed | Edit `.agents/skills/<skill>/`, run `python install.py`, then restart the agent. |
| The page is dark and I want light | Click ☀ at the top right. The page remembers it. |

---

## Credits
The ideas come from the "100 Powerful ChatGPT AI Commands" list: #1 `/visualize`, #2 `/handwritten`,
#3 `/infographic`, #4 `/diagram`, #5 `/flowchart`, #6 `/mindmap`, #7 `/xray`, #8 `/blueprint`,
#9 `/explodedview`, #10 `/thenvsnow`, #11 `/timeline`, #59 `/cheatsheet`. In that list, each command
is only a one-line prompt. This repo turns each one into a real, tested skill with a template and a
validator. `lavish` is a third-party skill by Kun Chen (MIT licence). `/explodedview` pages include
three.js (MIT licence, © three.js authors).
