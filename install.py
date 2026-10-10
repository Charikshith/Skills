#!/usr/bin/env python3
"""Install the skills in .agents/skills/ for Codex, Pi, Claude Code and Command Code.

Source of truth: <this repo>/.agents/skills/<skill>/  (Codex + Pi read this folder directly)
Copies go to:    .claude/skills/       (Claude Code)
                 .commandcode/skills/  (Command Code)

Usage:
  python install.py                       # sync copies inside this repo
  python install.py --target ../my-repo   # install into another project
  python install.py --agents claude,pi    # only some agents
  python install.py --global              # install for your user (all projects)
  python install.py --list                # show the skill names you can pick
  python install.py --skills flowchart    # only some skills (comma list), e.g. --skills flowchart,mindmap
Stdlib only. Copies, not symlinks, so it works on Windows without admin rights.
"""
import argparse, pathlib, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / ".agents" / "skills"

# agent -> (project folder, user/global folder)
AGENTS = {
    "codex":       (".agents/skills",      "~/.agents/skills"),
    "pi":          (".agents/skills",      "~/.pi/agent/skills"),
    "claude":      (".claude/skills",      "~/.claude/skills"),
    "commandcode": (".commandcode/skills", "~/.commandcode/skills"),
}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--target", default=str(HERE), help="project folder to install into (default: this repo)")
ap.add_argument("--agents", default=",".join(AGENTS), help=f"comma list from: {', '.join(AGENTS)}")
ap.add_argument("--global", dest="glob", action="store_true", help="install to user-level folders instead")
ap.add_argument("--skills", default="", help="comma list of skill names to install (default: all); see --list")
ap.add_argument("--list", action="store_true", help="list the skills you can install, then stop")
a = ap.parse_args()

agents = [x.strip() for x in a.agents.split(",") if x.strip()]
bad = [x for x in agents if x not in AGENTS]
if bad:
    sys.exit(f"unknown agent(s): {bad}. Use: {', '.join(AGENTS)}")

skills = sorted(p for p in SRC.iterdir() if (p / "SKILL.md").is_file())
if not skills:
    sys.exit(f"no skills found in {SRC}")
if a.list:
    for p in skills:
        print(p.name)
    sys.exit(0)
if a.skills:
    wanted = [x.strip().lstrip("/") for x in a.skills.split(",") if x.strip()]
    unknown = [w for w in wanted if w not in {p.name for p in skills}]
    if unknown:
        sys.exit(f"unknown skill(s): {unknown}. Run `python install.py --list` to see the names.")
    skills = [p for p in skills if p.name in wanted]

target = pathlib.Path(a.target).expanduser().resolve()
done = set()
for agent in agents:
    project_dir, user_dir = AGENTS[agent]
    dest_root = pathlib.Path(user_dir).expanduser() if a.glob else target / project_dir
    for skill in skills:
        dest = dest_root / skill.name
        if dest.resolve() == skill.resolve():
            print(f"[{agent}] {skill.name}: already in place ({dest})")
            continue
        if dest in done:
            print(f"[{agent}] {skill.name}: shared folder, already copied ({dest})")
            continue
        # Sync in place (never delete the folder itself: agents may hold a watch/lock on it on Windows)
        shutil.copytree(skill, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        keep = {p.relative_to(skill) for p in skill.rglob("*")}
        for p in sorted(dest.rglob("*"), key=lambda p: -len(p.parts)):   # remove files the source no longer has
            if p.relative_to(dest) not in keep and "__pycache__" not in p.parts:
                try: p.unlink() if p.is_file() else p.rmdir()
                except OSError as err: print(f"  note: could not remove stale {p} ({err})")
        done.add(dest)
        print(f"[{agent}] {skill.name}: installed -> {dest}")

if not a.glob and target != HERE:
    req = HERE / "requirements.txt"
    if req.exists() and not (target / "requirements.txt").exists():
        shutil.copy2(req, target / "requirements.txt")
        print(f"copied requirements.txt -> {target}")
print("done.")
