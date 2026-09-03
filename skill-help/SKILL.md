---
name: skill-help
description: Lists the Claude Code skills available to the user — both personal skills in ~/.claude/skills/ and project skills in the current repo's .claude/skills/ — showing each skill's name and description. Use this whenever the user asks to see, list, or browse available skills, or asks a broader question like "what skills do I have", "what can Claude do here", "is there a skill for this", or "what's installed" — not just when they explicitly say "list skills".
---

List the skills available to the user by running the bundled script, which scans both skill roots and parses each skill's `SKILL.md` frontmatter (`name` + `description`):

```bash
python "<skill-dir>/scripts/list_skills.py" "<project-root>"
```

Replace `<skill-dir>` with this skill's own directory (so the script itself can be located) and `<project-root>` with the user's current project root (usually the working directory) — the script looks for `.claude/skills/` under it.

The script prints two sections, personal and project skills, each as a `- **name**: description` list. Present that output to the user directly; don't re-summarize or reformat it further unless they ask for a different view (e.g. grouped by topic, or full SKILL.md contents for one specific skill — in that case just read that skill's SKILL.md directly instead of using the script).

If a section comes back empty (no personal or no project skills), that's expected — just omit or note it, not an error.
