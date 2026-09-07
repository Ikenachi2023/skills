#!/usr/bin/env python3
"""Safely invoke the Antigravity CLI (`agy`) to generate one image and copy it into the project.

Prints a single JSON object to stdout describing what happened. Never raises past main() --
every failure mode is reported as {"status": "error", ...} so the caller can read structured
output instead of parsing tracebacks.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

# agy's own --print-timeout default is 5 minutes. Give the subprocess a bit of headroom
# beyond that so we time out on our side only if agy itself fails to time out cleanly.
SUBPROCESS_TIMEOUT_SECONDS = 6 * 60


def find_brain_dir(conversation_id: str) -> Path:
    return Path.home() / ".gemini" / "antigravity-cli" / "brain" / conversation_id


def find_generated_image(brain_dir: Path):
    if not brain_dir.is_dir():
        return None, []
    candidates = [p for p in brain_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    if not candidates:
        return None, []
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0], candidates


def unique_destination(dest_dir: Path, filename_stem: str, extension: str) -> Path:
    candidate = dest_dir / f"{filename_stem}{extension}"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = dest_dir / f"{filename_stem}_{n}{extension}"
        if not candidate.exists():
            return candidate
        n += 1


def build_prompt(image_prompt: str, safe_md_text: str) -> str:
    # The safety-principles text is embedded directly rather than handed over as an @path
    # reference: agy's --add-dir is scoped to the *target project*, which does not include this
    # skill's own install directory where safe.md lives, so an @-reference to it would itself
    # get permission-denied before agy could ever read it. Inlining the text sidesteps that.
    #
    # Never name the underlying "Nano Banana" feature explicitly -- agy has, in testing,
    # mistaken that name for an external tool/library it should search the workspace for,
    # instead of recognizing it as its own built-in image generation capability.
    return (
        "Follow these safety principles for the rest of this task:\n\n"
        f"{safe_md_text}\n\n"
        "---\n\n"
        "Using your built-in image generation capability, generate the following image. "
        "Do not run any shell commands, do not write or execute any script, and do not try to "
        "move or copy the resulting file anywhere -- just generate it and tell me the file path "
        "where it was saved.\n\n"
        f"Image to generate: {image_prompt}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Directory passed to agy as --add-dir; agy is not permitted to touch anything outside it")
    parser.add_argument("--prompt", required=True, help="English description of the image to generate")
    parser.add_argument("--dest-dir", required=True, help="Project folder the final image should be copied into")
    parser.add_argument("--filename", required=True, help="Destination base filename (no extension) -- an English slug describing the image")
    parser.add_argument("--model", default=None, help="Optional agy --model override; omit to use agy's default")
    parser.add_argument("--safe-md", default=None, help="Path to the safety-principles file to hand to agy (defaults to safe.md next to this script's skill folder)")
    args = parser.parse_args()

    result = {"status": "error"}

    if shutil.which("agy") is None:
        result["error"] = "agy_not_found"
        result["message"] = "The `agy` command was not found on PATH. Antigravity CLI does not appear to be installed, or its install directory was not added to PATH."
        print(json.dumps(result))
        return

    project_root = Path(args.project_root).resolve()
    dest_dir = Path(args.dest_dir).resolve()
    safe_md_path = Path(args.safe_md).resolve() if args.safe_md else (Path(__file__).resolve().parent.parent / "safe.md")

    if not safe_md_path.is_file():
        result["error"] = "safe_md_missing"
        result["message"] = f"Expected safety-principles file not found at {safe_md_path}."
        print(json.dumps(result))
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    safe_md_text = safe_md_path.read_text(encoding="utf-8")
    prompt = build_prompt(args.prompt, safe_md_text)

    cmd = ["agy", "--add-dir", str(project_root), "--sandbox"]
    if args.model:
        cmd += ["--model", args.model]
    cmd += ["-p", prompt, "--output-format", "json"]

    start = time.time()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["message"] = f"agy did not respond within {SUBPROCESS_TIMEOUT_SECONDS} seconds."
        print(json.dumps(result))
        return
    duration = time.time() - start

    stdout = proc.stdout.strip()
    # agy sometimes writes a human-readable notice line before the JSON payload (e.g. when
    # actions were denied); the JSON itself is always the last line of stdout.
    json_line = stdout.splitlines()[-1] if stdout else ""
    try:
        agy_output = json.loads(json_line)
    except json.JSONDecodeError:
        result["status"] = "error"
        result["error"] = "unparseable_agy_output"
        result["message"] = "Could not parse agy's output as JSON."
        result["raw_stdout"] = stdout
        result["raw_stderr"] = proc.stderr.strip()
        print(json.dumps(result))
        return

    denied_actions = agy_output.get("denied_actions") or []
    conversation_id = agy_output.get("conversation_id")

    image_path, all_candidates = (None, [])
    if conversation_id:
        brain_dir = find_brain_dir(conversation_id)
        image_path, all_candidates = find_generated_image(brain_dir)

    if image_path is None:
        result["status"] = "error"
        result["error"] = "no_image_produced"
        result["message"] = "agy finished but no generated image file could be found."
        result["denied_actions"] = denied_actions
        result["agy_response"] = agy_output.get("response", "")
        result["duration_seconds"] = duration
        print(json.dumps(result))
        return

    dest_path = unique_destination(dest_dir, args.filename, image_path.suffix.lower())
    shutil.copyfile(image_path, dest_path)

    result["status"] = "success"
    result["saved_path"] = str(dest_path)
    result["source_path"] = str(image_path)
    result["denied_actions"] = denied_actions
    result["ambiguous_extra_files"] = [str(p) for p in all_candidates[1:]] if len(all_candidates) > 1 else []
    result["duration_seconds"] = duration
    print(json.dumps(result))


if __name__ == "__main__":
    main()
