"""Builds throwaway git repo fixtures used by the commit-skill evals.

Run this once (or whenever fixtures need to be regenerated) to (re)create
the fixture repos under evals/fixtures/. Each fixture repo has an initial
commit and then some staged/unstaged working-tree changes, simulating a
piece of work in progress that /commit should be run against.
"""
import shutil
import subprocess
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, shell=False)


def git_init(repo):
    run(["git", "init", "-q"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    run(["git", "config", "user.name", "Test User"], repo)


def commit(repo, message, date=None):
    env_cmd = ["git", "commit", "-q", "-m", message]
    if date:
        run(["git", "commit", "-q", "-m", message, "--date", date], repo)
    else:
        run(env_cmd, repo)


def build_typo_fix():
    repo = FIXTURES_DIR / "typo-fix"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git_init(repo)
    (repo / "greet.py").write_text(
        "def greet(name):\n"
        "    # retuns a friendly greeting\n"
        "    return f'Hello, {name}!'\n"
    )
    run(["git", "add", "greet.py"], repo)
    commit(repo, "Add greet function")

    (repo / "greet.py").write_text(
        "def greet(name):\n"
        "    # returns a friendly greeting\n"
        "    return f'Hello, {name}!'\n"
    )
    run(["git", "add", "greet.py"], repo)


def build_auth_decision():
    repo = FIXTURES_DIR / "auth-decision"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git_init(repo)
    (repo / "server.py").write_text(
        "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef index():\n    return 'ok'\n"
    )
    run(["git", "add", "server.py"], repo)
    commit(repo, "Initial Flask app skeleton")

    (repo / "auth.py").write_text(
        "import jwt\nimport datetime\n\nSECRET = 'change-me'\n\n\n"
        "def issue_token(user_id):\n"
        "    payload = {\n"
        "        'sub': user_id,\n"
        "        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12),\n"
        "    }\n"
        "    return jwt.encode(payload, SECRET, algorithm='HS256')\n\n\n"
        "def verify_token(token):\n"
        "    return jwt.decode(token, SECRET, algorithms=['HS256'])\n"
    )
    run(["git", "add", "auth.py"], repo)


def build_long_conversation():
    repo = FIXTURES_DIR / "pagination-refactor"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    git_init(repo)
    (repo / "api.py").write_text(
        "def list_items(items, page=1, page_size=20):\n"
        "    start = (page - 1) * page_size\n"
        "    return items[start:start + page_size]\n"
    )
    run(["git", "add", "api.py"], repo)
    commit(repo, "Add offset-based pagination", date="2026-08-20T10:00:00")

    (repo / "api.py").write_text(
        "def list_items(items, cursor=None, page_size=20):\n"
        "    start = 0\n"
        "    if cursor is not None:\n"
        "        start = next((i + 1 for i, it in enumerate(items) if it['id'] == cursor), 0)\n"
        "    page = items[start:start + page_size]\n"
        "    next_cursor = page[-1]['id'] if len(page) == page_size else None\n"
        "    return page, next_cursor\n"
    )
    run(["git", "add", "api.py"], repo)


if __name__ == "__main__":
    FIXTURES_DIR.mkdir(exist_ok=True)
    build_typo_fix()
    build_auth_decision()
    build_long_conversation()
    print(f"Fixtures built under {FIXTURES_DIR}")
