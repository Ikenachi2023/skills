---
name: nanobananer
description: Generates a new image (illustration, icon, texture, logo, artwork, picture) into the current project by delegating to the Antigravity CLI (`agy`)'s built-in image generation. Trigger whenever the user explicitly asks to generate, create, draw, or make an image, icon, texture, logo, or piece of artwork as a file — e.g. "generate an image of X", "画像を生成して", "〇〇のアイコンを作って", "このテクスチャを作って". Do not use this for editing or analyzing an existing image, for charts/diagrams/data visualizations (those have their own skills), or when the user's intent is ambiguous about whether they want a generated file at all.
---

# nanobananer

Delegates image generation to Antigravity CLI (`agy`), which has a built-in image generation
capability (internally, a `generate_image` tool). `agy` is a separate agentic CLI with its own
filesystem access and permission system — treat it the way you'd treat any external agent you
don't fully control: hand it the minimum scope it needs, and verify what it actually did.

## The absolute rule: agy never touches anything outside the project

`agy` gets `--add-dir <project-root>` and never `--dangerously-skip-permissions`. Without that
flag, agy's own permission system auto-denies (not prompts — headless mode can't prompt) any
tool action outside the granted directory, and reports it in a `denied_actions` field. This has
been verified empirically: a read attempt outside `--add-dir` came back denied with an empty
response, no data leaked. Never add `--dangerously-skip-permissions` to work around a denial —
if something legitimate is getting denied, that means the design below needs to change, not that
the safety flag should go.

Do not ask agy to save the image directly to a path in your project. Asking for an explicit
destination path makes agy try to run a shell command (`mv`/a script) to get it there, and that
command execution requires permission it doesn't have under this design, so the whole generation
fails. Instead, let agy generate and save wherever it wants (its own internal storage) and
report the path back — then copy the file into the project yourself, since you already have full
filesystem access and don't need agy's permission for that.

Everything above is implemented in `scripts/generate_image.py` — use it rather than shelling out
to `agy` directly, so these constraints can't be accidentally dropped:

```
python "<skill-dir>/scripts/generate_image.py" \
  --project-root "<project-root>" \
  --prompt "<English description of the image>" \
  --dest-dir "<folder the image should land in>" \
  --filename "<english_slug_no_extension>"
```

`<skill-dir>` is this skill's own directory (so `--safe-md` can default to `safe.md` next to it).
The script prints one JSON object to stdout: `{"status": "success", "saved_path": ..., "denied_actions": [...], ...}`
on success, or `{"status": "error"/"timeout", "message": ..., ...}` otherwise.

**If `denied_actions` is non-empty**, even on an otherwise-successful run, tell the user plainly
that agy attempted an action outside its permitted scope and it was blocked — don't bury this.
It's a signal something about the request or the environment is behaving unexpectedly.

**If `status` is `error` with `error: "agy_not_found"`**, tell the user Antigravity CLI isn't
installed or isn't on PATH, and stop — don't fall back to some other image-generation method
without being asked; the user chose this tool.

## Writing the prompt

Write `--prompt` in English regardless of the conversation's language — image generation models
are overwhelmingly trained on English prompts and style vocabulary (e.g. "pixel art",
"isometric", "cel-shaded") lands more reliably in English. Do not mention "Nano Banana" by name
anywhere in the prompt — in testing, agy misread that as a reference to some external
tool/library it should search the workspace for, rather than recognizing its own built-in
capability, and got confused. Just describe the image you want.

Decide and generate immediately for straightforward requests. Ask one clarifying question first
only when something that would substantially change the output is genuinely unclear — composition,
style, aspect ratio/use-case (e.g. "icon" vs "background" vs "texture"). Don't interrogate the
user over minor details you can reasonably infer.

If the request implies transparency (e.g. "a logo", "an icon") and the result comes back as a
non-transparent format like JPEG, mention that once — don't silently hand over a JPEG when
transparency was clearly wanted, and don't try to force a fake transparency conversion either
(a JPEG never had an alpha channel to recover).

For multiple images in one request (e.g. "generate 3 icon options"), call the script once per
image rather than asking agy for all of them in a single call — each call gets its own isolated
agy conversation and brain folder, which keeps failures and file identification unambiguous.

## Choosing `--dest-dir` and `--filename`

Figure out where generated images belong the same way you'd figure out any other file placement:
look at the conversation, `CLAUDE.md`, and the existing project structure (an `assets/`,
`static/`, `public/images/`, or similar folder already in use). If nothing gives you a clear
answer, ask the user — don't invent a new folder convention unprompted.

`--filename` should be a descriptive English slug (e.g. `stone_texture`, `logo_dark_mode`) with
no extension — the script preserves whatever extension agy actually produced. If a file with
that name already exists at the destination, the script appends `_2`, `_3`, etc. automatically;
you don't need to check for collisions yourself.

## Model selection

Don't pass `--model`; let agy use its default. If a run's `agy_response`/error indicates the
selected model doesn't have image generation available, tell the user and ask whether to pin a
specific model (check `agy models` for one known to support image generation) before retrying.

## If the result doesn't match what the user wanted

Ask what specifically is off (color, composition, style, mood) rather than regenerating blindly,
then fold that into a revised `--prompt` and call the script again. Don't loop indefinitely on
vague "no, different" feedback — get at least one concrete direction to change first.

## Timeouts

The script waits up to 6 minutes for agy (agy's own default response budget is 5 minutes; the
extra minute is slack for the script itself). If `status` comes back `timeout`, report that
plainly and let the user decide whether to retry — don't auto-retry, since a slow run may well be
an agy-side issue that a retry won't fix.
