---
name: draw
description: Router for structure visuals. Picks the right skill (flowchart, diagram, mindmap, timeline, or visualize as fallback) from the request and hands off to it. Use whenever the user types /draw, or asks to "draw", "sketch" or "lay out" something without saying which kind of picture, e.g. "draw how login works", "sketch the onboarding", "show how X is built". Skip when the user already names a type (/flowchart, /diagram, /mindmap, /timeline) — use that skill directly.
---

# /draw — pick the right picture, then make it

This skill makes no page itself. It chooses one skill, says why in one line, and follows that skill's `SKILL.md` for the rest.

## Pick by the question the request asks

| The request is about… | Use | Tell-tale words |
|---|---|---|
| Steps in order, choices, "what happens if" | `/flowchart` | process, workflow, approval, troubleshoot, if/else, loop |
| Parts and how they connect (things, not steps) | `/diagram` | architecture, system, network, pipeline, components, how X is built |
| Ideas around one topic, no order or flow | `/mindmap` | overview, brainstorm, concepts, break X into parts, study notes |
| Events along dates | `/timeline` | history, evolution, over time, chronology, key dates |
| None of the above (cycle, layers, scene, "how X works") | `/visualize` | explain, illustrate, show me how |

## Tie-breakers

- Time or logic runs through it → flowchart. Components and links → diagram. A tree of ideas → mindmap.
- Dates are the backbone → timeline, even if it reads like a process.
- A pipeline (A → B → C) with no decisions → diagram. With decisions or retries → flowchart.
- Still torn after one pass → pick the closer one. Do not ask the user.

## Out of scope

Physical objects (blueprint, exploded view, x-ray) and number-driven pages (infographic, then-vs-now, cheatsheet) have their own commands. If asked for one, say so and use that skill.

## Steps

1. Read the request and pick one row above.
2. Reply with one line: `Using /<skill> — <reason>. Say "use /<other>" to switch.`
3. Load that skill's `SKILL.md` and do exactly what it says, including its validator. Pass the user's request and any `handwritten` style flag through unchanged.
