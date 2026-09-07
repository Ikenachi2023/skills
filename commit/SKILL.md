---
name: commit
description: Create a git commit whose message always has three fixed sections — Implementation (what changed), Decisions (decisions worth remembering for future development), and Discussion (the user's questions and how they were resolved in conversation). Use this whenever the user runs /commit, or asks to "commit this", "コミットして", or otherwise wants their work committed — this skill's structured format is the expected commit style for this user and should be used instead of a plain one-line commit message, even if they don't spell out the three sections explicitly.
---

# commit

Produce a git commit whose message documents not just *what* changed, but the
reasoning behind it. A commit message written from the diff alone loses
everything that happened in conversation — decisions the user made, tradeoffs
they considered, questions they asked before locking in an approach. Six
months from now, `git log` should be able to answer "why did we do it this
way?" without anyone needing to dig up this chat.

## Format

Every commit message uses exactly these three sections, in this order, even
when a section has nothing to report (write `特になし` rather than omitting
the heading — a consistent shape makes the log skimmable and makes "nothing
happened here" a meaningful, greppable signal rather than an absence):

```
<type>: <short, imperative title describing the change>

## Implementation
<What was implemented/changed, concisely — a few lines, not a diff narration>

## Decisions
<Decisions made during this work that matter for future development —
architecture choices, rejected alternatives, constraints discovered, naming
conventions settled on. Write 特になし if nothing rose to that level.>

## Discussion
<Q&A形式（Q: ... / A: ...）で、何を問い、何が決まったかを記録する。
Write 特になし if the work proceeded without any such back-and-forth.>

Co-Authored-By: Claude <noreply@anthropic.com>
```

Always pass the message via a heredoc (see the repo-wide git commit
instructions) so the multi-line structure survives intact.

### Title prefix

Prefix the title with a Conventional Commits-style type, chosen from the
actual diff rather than defaulted to `fix:`:

- `fix:` — a bug fix
- `feat:` — new functionality
- `refactor:` — restructuring without behavior change
- `docs:` — documentation/comments only
- `chore:` — tooling, config, dependencies, cleanup
- `test:` — test-only changes

Pick whichever fits the diff; when a change spans types, pick the one that
best describes its main intent.

## Filling in each section

**Implementation** comes from `git diff --staged` (or `git diff` if nothing is
staged yet) — summarize the change itself, briefly. This is the one section
that's just describing code, so keep it short; the other two sections are
where this skill adds value beyond a normal commit message.

**Decisions** and **Discussion** come from the conversation, not the
diff. Look back over the *entire conversation since the previous commit* —
run `git log -1 --format=%cI` to see when that commit landed, and treat
everything discussed after that point as in scope. Filter for relevance:
skip small talk or instructions unrelated to this change, but err toward
including anything that touches why the code ended up the way it did.

- **Decisions** is about durable decisions — the kind of thing a future
  contributor (including a future you) would want to know before touching
  this code again. A decision confirmed without much discussion still
  belongs here if it constrains future work.
- **Discussion** is about *back-and-forth that shaped the outcome* — a question
  that got weighed against alternatives, a proposal that got pushed back on,
  a direction that changed mid-conversation. A plain instruction-and-done
  exchange ("greet.pyのtypo直して" → fixed) has no such shaping to record,
  even though words were technically exchanged — write 特になし for it
  rather than restating the request as if it were a dialogue. Only reach
  for content here when there was actually something to converge on.
- Never paste the user's chat messages verbatim. Rewrite each exchange as a
  Q&A pair — `Q: <何を問うたか>` / `A: <何が決まったか、なぜか>` — summarizing
  in neutral, polite business Japanese (敬語・丁寧語). Casual speech, slang,
  or offhand remarks (e.g. 「これダサくね？」「〜っしょ」「めんどいから」)
  must be rephrased into their professional equivalent conveying the same
  intent (e.g. 「見た目が洗練されていないと感じたため」) — the log is a
  durable record other engineers will read, not a chat transcript.

A useful test: if you removed this section, would a future reader lose
information they'd otherwise have wanted? If not, it's 特になし.

Keep the message light — this is a summary, not a transcript. Compress each
entry to one line wherever the point survives; don't record every exchange
that happened, only the ones that changed what the code or the reader's
understanding ends up being. For instance, a question that was purely
clarifying ("〇〇って何？" that led to adding an explanatory comment, with no
alternative weighed) doesn't need its own Q&A pair — fold it into
Implementation as "わかりにくい箇所にコメントを追加" instead of narrating the
question-and-answer. Reserve full Q&A pairs for exchanges where a decision
or direction was actually contested or chosen among alternatives.

These two sections often overlap in substance (a decision usually emerged
from some dialogue) — that's fine. **Decisions** is the conclusion;
**Discussion** is the path that led there.

## Staging

Follow the normal staging convention: commit whatever is already staged. If
nothing is staged, stage the specific files that changed for this piece of
work by name (never `git add -A` / `git add .`), following the repo-wide git
safety instructions — don't sweep up unrelated untracked files.

## Before committing

Run `git status`, `git diff --staged` (and `git diff` for anything unstaged
that should be included), and `git log -1` in parallel to gather everything
above. Only create the commit after the message is fully drafted — don't
commit first and amend after, per the repo-wide instruction to avoid
`--amend` on non-trivial edits.
