#!/usr/bin/env python3
"""List available Claude Code skills (personal + project) with their name and description.

Usage: python list_skills.py [project_dir]
  project_dir defaults to the current working directory.
"""
import os
import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def find_skill_md(skill_dir):
    path = os.path.join(skill_dir, "SKILL.md")
    return path if os.path.isfile(path) else None


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    desc_m = re.search(r"^description:\s*(.+?)(?=\n\S+:|\Z)", fm, re.DOTALL | re.MULTILINE)
    name = name_m.group(1).strip() if name_m else None
    description = " ".join(desc_m.group(1).split()) if desc_m else ""
    return name, description


def scan(skills_root):
    results = []
    if not os.path.isdir(skills_root):
        return results
    for entry in sorted(os.listdir(skills_root)):
        skill_dir = os.path.join(skills_root, entry)
        if not os.path.isdir(skill_dir):
            continue
        md_path = find_skill_md(skill_dir)
        if not md_path:
            continue
        parsed = parse_frontmatter(md_path)
        if not parsed:
            continue
        name, description = parsed
        results.append((name or entry, description, skill_dir))
    return results


def main():
    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    personal_root = os.path.expanduser("~/.claude/skills")
    project_root = os.path.join(project_dir, ".claude", "skills")

    personal = scan(personal_root)
    project = scan(project_root)

    if not personal and not project:
        print("スキルが見つかりませんでした。")
        return

    if personal:
        print(f"## 個人スキル ({personal_root})\n")
        for name, description, path in personal:
            print(f"- **{name}**: {description}")
        print()

    if project:
        print(f"## プロジェクトスキル ({project_root})\n")
        for name, description, path in project:
            print(f"- **{name}**: {description}")


if __name__ == "__main__":
    main()
