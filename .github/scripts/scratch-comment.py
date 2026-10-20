#!/usr/bin/env python3
"""Keep one pull request comment with the scratch build table.

The comment is <!-- ftuna-scratch RUN_ID --> plus a markdown table.
Parallel jobs update their own row. A write is kept only when a fresh
read still shows that run and every row that write intended. A job from
an older run leaves the newer table alone.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time

MARKER = "<!-- ftuna-scratch"
RUN_ID = re.compile(r"<!-- ftuna-scratch (\d+) -->")
ROW = re.compile(r"^\| `([^`]+)` \| ([^|]*) \| ([^|]*) \|$")
OPEN = {"queued", "building"}
STATUSES = OPEN | {"success", "failed", "cancelled"}
Row = tuple[str, str, str]


class CommentError(Exception):
    pass


class MissingRecipe(CommentError):
    pass


def clean_cell(value: str) -> str:
    value = value.replace("\r", " ").replace("\n", " ").replace("|", "/").replace("`", "'")
    value = re.sub(r"\s+", " ", value).strip()
    return value[:500]


def parse(body: str) -> tuple[str, list[Row]]:
    body = body.replace("\r\n", "\n")
    found = RUN_ID.search(body)
    run_id = found.group(1) if found else ""
    rows: list[Row] = []
    for line in body.splitlines():
        match = ROW.match(line.strip())
        if not match:
            continue
        rows.append((match.group(1), match.group(2).strip(), match.group(3).strip()))
    return run_id, rows


def render(run_id: str, rows: list[Row]) -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    logs = f"{server}/{repo}/actions/runs/{run_id}"
    lines = [
        f"<!-- ftuna-scratch {run_id} -->",
        "",
        f"[Build logs]({logs})",
        "",
        "| Recipe | Status | Result |",
        "| --- | --- | --- |",
    ]
    for recipe, status, result in rows:
        lines.append(f"| `{recipe}` | {status} | {result} |")
    lines.append("")
    return "\n".join(lines)


def apply_update(rows: list[Row], recipe: str, status: str, result: str, if_open: bool) -> tuple[list[Row], bool]:
    found = False
    changed = False
    out: list[Row] = []
    for current in rows:
        if current[0] != recipe:
            out.append(current)
            continue
        found = True
        if if_open and current[1] not in OPEN:
            out.append(current)
            continue
        updated = (recipe, status, result)
        if updated != current:
            changed = True
        out.append(updated)
    if not found:
        raise MissingRecipe(f"recipe {recipe} is not in the scratch comment")
    return out, changed


def api(method: str, path: str, payload: dict | None = None, paginate: bool = False) -> object:
    cmd = ["gh", "api", "--method", method]
    if paginate:
        cmd.append("--paginate")
    cmd.append(path)
    text = None
    if payload is not None:
        cmd.extend(["--input", "-"])
        text = json.dumps(payload)
    proc = subprocess.run(cmd, input=text, text=True, capture_output=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise CommentError(detail or f"gh api {method} {path} failed")
    raw = proc.stdout.strip()
    if not raw:
        return None
    return json.loads(raw)


def repo_path(path: str) -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise CommentError("GITHUB_REPOSITORY is required")
    return f"repos/{repo}{path}"


def find_comment(pr: str) -> dict | None:
    found = api("GET", repo_path(f"/issues/{pr}/comments?per_page=100"), paginate=True)
    if not isinstance(found, list):
        raise CommentError("comment list was not a list")
    for comment in found:
        body = comment.get("body") or ""
        if MARKER in body:
            return comment
    return None


def get_comment(comment_id: int) -> dict:
    found = api("GET", repo_path(f"/issues/comments/{comment_id}"))
    if not isinstance(found, dict):
        raise CommentError("comment was not an object")
    return found


def save_comment(pr: str, body: str, comment_id: int | None) -> int:
    if comment_id is None:
        created = api("POST", repo_path(f"/issues/{pr}/comments"), {"body": body})
        if not isinstance(created, dict) or "id" not in created:
            raise CommentError("creating the scratch comment returned no id")
        return int(created["id"])
    api("PATCH", repo_path(f"/issues/comments/{comment_id}"), {"body": body})
    return comment_id


def require_digits(value: str, label: str) -> str:
    if not value.isdigit():
        raise CommentError(f"{label} is required")
    return value


def init(pr: str, run_id: str, recipes: list[str]) -> None:
    rows = [(recipe, "queued", "") for recipe in recipes]
    body = render(run_id, rows)
    for attempt in range(1, 9):
        try:
            existing = find_comment(pr)
            comment_id = save_comment(pr, body, int(existing["id"]) if existing else None)
            got_run, got_rows = parse(get_comment(comment_id).get("body") or "")
            if got_run == run_id and got_rows == rows:
                print(body, end="")
                return
        except (CommentError, json.JSONDecodeError, KeyError, ValueError) as exc:
            print(f"scratch comment: {exc}", file=sys.stderr)
        time.sleep(0.25 * attempt + random.random() * 0.25)
    raise CommentError("could not post the scratch comment")


def update(pr: str, run_id: str, recipe: str, status: str, result: str, if_open: bool) -> None:
    result = clean_cell(result)
    # Jobs start together. Spread the first read so they do not all write one stale table.
    if os.environ.get("SCRATCH_COMMENT_SPREAD") == "1":
        time.sleep(random.uniform(0.0, 3.0))
    for attempt in range(1, 61):
        try:
            existing = find_comment(pr)
            if existing is None:
                raise CommentError("scratch comment is not up yet")
            comment_id = int(existing["id"])
            current_run, rows = parse(existing.get("body") or "")
            if current_run != run_id:
                print(f"scratch comment belongs to run {current_run or 'unknown'}, not {run_id}", file=sys.stderr)
                return
            rows, changed = apply_update(rows, recipe, status, result, if_open)
            if not changed:
                return
            body = render(run_id, rows)
            save_comment(pr, body, comment_id)
            got_run, got_rows = parse(get_comment(comment_id).get("body") or "")
            if got_run == run_id and got_rows == rows:
                print(f"{recipe} {status} {result}".rstrip())
                return
        except MissingRecipe:
            raise
        except CommentError as exc:
            print(f"scratch comment: {exc}", file=sys.stderr)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            print(f"scratch comment: {exc}", file=sys.stderr)
        time.sleep(min(4.0, 0.15 * attempt) + random.random())
    raise CommentError("could not update the scratch comment")


def read_recipes(path: str) -> list[str]:
    recipes: list[str] = []
    seen: set[str] = set()
    with open(path) as handle:
        for line in handle:
            recipe = line.strip()
            if not recipe or recipe in seen:
                continue
            if "`" in recipe or "|" in recipe or "\n" in recipe:
                raise CommentError(f"recipe id cannot be shown in the table: {recipe!r}")
            seen.add(recipe)
            recipes.append(recipe)
    if not recipes:
        raise CommentError("no recipes to list")
    return recipes


def self_test() -> None:
    os.environ["GITHUB_REPOSITORY"] = "acme/recipes"
    os.environ["GITHUB_SERVER_URL"] = "https://github.com"
    rows: list[Row] = [
        ("github.com/abseil/abseil-cpp", "failed", "build failed"),
        ("github.com/cisco/openh264", "success", "https://scratchpad-repo.ftuna.eu/abc/name/"),
    ]
    body = render("99", rows)
    assert parse(body) == ("99", rows)
    assert "[Build logs](https://github.com/acme/recipes/actions/runs/99)" in body
    queued = [("github.com/abseil/abseil-cpp", "queued", ""), ("github.com/cisco/openh264", "building", "")]
    updated, changed = apply_update(queued, "github.com/cisco/openh264", "success", "https://example.test/a", False)
    assert changed
    assert updated[0] == queued[0]
    assert updated[1][1] == "success"
    kept, changed = apply_update(updated, "github.com/cisco/openh264", "failed", "build failed", True)
    assert not changed
    assert kept[1][1] == "success"
    opened, changed = apply_update(queued, "github.com/abseil/abseil-cpp", "failed", "build failed", True)
    assert changed and opened[0][1] == "failed"
    try:
        apply_update(queued, "missing", "failed", "", False)
    except CommentError:
        pass
    else:
        raise AssertionError("missing recipe should fail")
    assert clean_cell("a|b\nc") == "a/b c"
    many = [(f"github.com/acme/pkg{i}", "queued", "") for i in range(20)]
    for i in range(20):
        many, changed = apply_update(many, f"github.com/acme/pkg{i}", "success", f"https://example.test/{i}", False)
        assert changed
    assert [status for _, status, _ in many] == ["success"] * 20
    print("ok")


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--self-test":
        self_test()
        return 0
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init")
    init_cmd.add_argument("--pr", default=os.environ.get("PR_NUMBER", ""))
    init_cmd.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    init_cmd.add_argument("--recipes", required=True)

    update_cmd = sub.add_parser("update")
    update_cmd.add_argument("--pr", default=os.environ.get("PR_NUMBER", ""))
    update_cmd.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    update_cmd.add_argument("--recipe", default=os.environ.get("RECIPE", ""))
    update_cmd.add_argument("--status", required=True)
    update_cmd.add_argument("--result", default="")
    update_cmd.add_argument("--if-open", action="store_true")

    args = parser.parse_args(argv)
    try:
        pr = require_digits(args.pr, "pull request number")
        run_id = require_digits(args.run_id, "run id")
        if args.command == "init":
            init(pr, run_id, read_recipes(args.recipes))
            return 0
        if args.status not in STATUSES:
            raise CommentError(f"unknown status {args.status}")
        if not args.recipe or "`" in args.recipe or "|" in args.recipe:
            raise CommentError("recipe is required")
        update(pr, run_id, args.recipe, args.status, args.result, args.if_open)
        return 0
    except CommentError as exc:
        print(f"scratch comment: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
