#!/usr/bin/env python3
"""Open one pull request per github.com recipe whose upstream moved.

Only github.com/<owner>/<repo> recipes are checked. Every *.yaml file in
that directory is a recipe, and they share one pull request. Each file
keeps its own pinned commit. Each check is one ls-remote of HEAD and tags,
with redirects and git config ignored so the request cannot be sent to
another host. When the pinned hash is a version tag, follow the newest tag
in that series. Otherwise follow the default branch tip. One open pull
request per repository is kept. A later upstream commit updates that same
request. If the request was left open and both repositories moved, it is
rebased onto the latest base and force-pushed.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

HOST = "github.com"
NAME = re.compile(r"[A-Za-z0-9_.-]{1,100}")
COMMIT_LINE = re.compile(r"(?m)^commit:\s*['\"]?([0-9a-fA-F]{40})['\"]?\s*$")
VERSION = re.compile(
    r"^(?:(?P<prefix>[A-Za-z0-9_.-]+)/)?"
    r"v?(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?"
    r"(?P<pre>[-+][0-9A-Za-z.-]+)?$"
)


@dataclass
class Tag:
    name: str
    sha: str


@dataclass
class Plan:
    mode: str
    old: str
    new: str
    from_tag: str | None
    to_tag: str | None
    upstream_branch: str


@dataclass
class FileUpdate:
    relative: str
    plan: Plan


def git_net(*args: str) -> list[str]:
    return ["git", "-c", "http.followRedirects=false", *args]


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or f"{args[0]} exited {result.returncode}")
    return result


def gh_json(args: list[str]) -> object:
    result = run(["gh", *args])
    return json.loads(result.stdout)


def version_info(name: str) -> tuple[str, tuple[int, int, int, int]] | None:
    match = VERSION.fullmatch(name)
    if not match:
        return None
    pre = match.group("pre") or ""
    stable = 0 if pre.startswith("-") else 1
    key = (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch") or 0),
        stable,
    )
    return match.group("prefix") or "", key


def series_prefix(name: str) -> str:
    info = version_info(name)
    if info:
        return info[0]
    return name.split("/", 1)[0] if "/" in name else ""


def read_commit(text: str) -> str:
    match = COMMIT_LINE.search(text)
    if not match:
        raise RuntimeError("recipe yaml has no 40-character commit hash")
    return match.group(1)


def replace_commit(text: str, old: str, new: str) -> str:
    pattern = re.compile(
        rf"(?<![0-9a-fA-F]){re.escape(old)}(?![0-9a-fA-F])",
        re.IGNORECASE,
    )
    updated, count = pattern.subn(new, text)
    if count == 0:
        raise RuntimeError(f"commit {old} was not found in the recipe yaml")
    return updated


def github_url(owner: str, repo: str) -> str:
    if not NAME.fullmatch(owner) or not NAME.fullmatch(repo):
        raise RuntimeError(f"refusing to contact a host other than {HOST}")
    return f"https://{HOST}/{owner}/{repo}.git"


def remote_host(url: str) -> str:
    if url.startswith("git@"):
        host = url.split("@", 1)[1].split(":", 1)[0]
        return host.lower()
    return (urlparse(url).hostname or "").lower()


def require_github_origin() -> None:
    url = run(["git", "remote", "get-url", "origin"]).stdout.strip()
    host = remote_host(url)
    if host != HOST:
        raise SystemExit(f"refusing origin host {host or url}; only {HOST} is allowed")


def list_refs(owner: str, repo: str) -> tuple[str, str, list[Tag]]:
    """List HEAD and tags with one upload-pack request. No objects are downloaded."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env.pop("GIT_DIR", None)
    env.pop("GIT_CONFIG", None)
    result = subprocess.run(
        [
            "git",
            "-c",
            "protocol.version=2",
            "-c",
            "http.followRedirects=false",
            "ls-remote",
            "--symref",
            github_url(owner, repo),
            "HEAD",
            "refs/tags/*",
        ],
        text=True,
        capture_output=True,
        env=env,
        cwd="/",
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "ls-remote failed").strip()
        raise RuntimeError(detail)
    return parse_remote_refs(result.stdout)


def parse_remote_refs(text: str) -> tuple[str, str, list[Tag]]:
    branch = ""
    head = ""
    commits: dict[str, str] = {}
    peeled: set[str] = set()
    for line in text.splitlines():
        if line.startswith("ref:"):
            ref, name = line.split("\t", 1)
            prefix = "ref: refs/heads/"
            if name == "HEAD" and ref.startswith(prefix):
                branch = ref[len(prefix) :]
            continue
        sha, ref = line.split("\t", 1)
        if ref == "HEAD":
            head = sha
            continue
        tag_prefix = "refs/tags/"
        if not ref.startswith(tag_prefix):
            continue
        if ref.endswith("^{}"):
            name = ref[len(tag_prefix) : -3]
            commits[name] = sha
            peeled.add(name)
        else:
            name = ref[len(tag_prefix) :]
            if name not in peeled:
                commits[name] = sha
    if not head or not branch:
        raise RuntimeError(f"{HOST} did not advertise a default branch")
    tags = [Tag(name, sha) for name, sha in commits.items()]
    return branch, head, tags


def choose_tag(tags: list[Tag], pin: str) -> tuple[Tag, Tag] | None:
    pin_l = pin.lower()
    matched = [tag for tag in tags if tag.sha.lower() == pin_l]
    if not matched:
        return None
    parsed = []
    for tag in matched:
        info = version_info(tag.name)
        if info:
            parsed.append((tag, info))
    anchor = parsed[0][0] if parsed else matched[0]
    if not parsed:
        # An unversioned tag still means "follow tags", but ordering those
        # needs tag dates. Leave the pin where it is instead of downloading them.
        return anchor, anchor
    prefix = series_prefix(anchor.name)
    pool = []
    for tag in tags:
        info = version_info(tag.name)
        if info and info[0] == prefix:
            pool.append((info[1], tag.name, tag))
    best = max(pool)[2]
    current = max((info[1], tag.name, tag) for tag, info in parsed)[2]
    return current, best


def plan_from_refs(branch: str, head: str, tags: list[Tag], pin: str, label: str) -> Plan | None:
    chosen = choose_tag(tags, pin)
    prefix = f"  {label}: " if label else "  "
    if chosen:
        current, best = chosen
        if best.sha.lower() == pin.lower():
            note = ""
            if head.lower() != pin.lower():
                note = f"; {branch} is at {head[:12]} and is ignored because this pin is a tag"
            print(f"{prefix}up to date (tag {current.name}){note}")
            return None
        return Plan(
            mode="tag",
            old=pin,
            new=best.sha,
            from_tag=current.name,
            to_tag=best.name,
            upstream_branch=branch,
        )

    if head.lower() == pin.lower():
        print(f"{prefix}up to date ({branch})")
        return None
    return Plan(
        mode="commit",
        old=pin,
        new=head,
        from_tag=None,
        to_tag=None,
        upstream_branch=branch,
    )


def pending_updates(owner: str, repo: str, recipe: Path, root: Path) -> list[FileUpdate]:
    files = sorted(path for path in recipe.glob("*.yaml") if path.is_file())
    if not files:
        raise RuntimeError(f"{recipe} has no recipe yaml")
    branch, head, tags = list_refs(owner, repo)
    out = []
    for path in files:
        pin = read_commit(path.read_text())
        plan = plan_from_refs(branch, head, tags, pin, path.name)
        if plan is None:
            continue
        out.append(FileUpdate(path.relative_to(root).as_posix(), plan))
    return out


def recipe_dirs(root: Path, recipe_filter: str) -> list[Path]:
    found = []
    seen: set[str] = set()
    for manifest in sorted(root.glob(f"{HOST}/*/*/*.yaml")):
        parts = manifest.relative_to(root).parts
        if len(parts) != 4 or parts[0] != HOST:
            continue
        if not NAME.fullmatch(parts[1]) or not NAME.fullmatch(parts[2]):
            continue
        parent = manifest.parent
        key = parent.relative_to(root).as_posix()
        if key in seen:
            continue
        seen.add(key)
        found.append(parent)
    filt = recipe_filter.strip().strip("/")
    if not filt:
        return found
    if filt.startswith(f"{HOST}/"):
        filt = filt[len(HOST) + 1 :]
    else:
        first = filt.split("/", 1)[0]
        if "." in first:
            raise SystemExit(f"refusing {first}; only {HOST} recipes are checked")
    if not selected_recipe(filt):
        raise SystemExit(f"no recipe at {HOST}/{filt}")
    selected = [path for path in found if path.relative_to(root).as_posix() == f"{HOST}/{filt}"]
    if not selected:
        raise SystemExit(f"no recipe at {HOST}/{filt}")
    return selected


def selected_recipe(filt: str) -> bool:
    parts = filt.split("/")
    return len(parts) == 2 and all(NAME.fullmatch(part) for part in parts)


def branch_for(recipe: Path, root: Path) -> str:
    owner, repo = recipe.relative_to(root).parts[1:3]
    return f"update/{owner}/{repo}"


def github_repository() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        return repo
    info = gh_json(["repo", "view", "--json", "nameWithOwner"])
    if not isinstance(info, dict) or not info.get("nameWithOwner"):
        raise RuntimeError("could not resolve the recipes repository")
    return str(info["nameWithOwner"])


def file_at_ref(relative: str, sha: str) -> str | None:
    if not relative.startswith(f"{HOST}/"):
        raise RuntimeError(f"refusing to update a recipe outside {HOST}")
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{github_repository()}/contents/{relative}",
            "-f",
            f"ref={sha}",
            "--jq",
            ".content",
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return base64.b64decode(result.stdout).decode()
    except ValueError:
        return None


def declined_files(branch: str, base: str, files: list[FileUpdate]) -> bool:
    """True when the newest unmerged closed PR already proposed these commits."""
    listed = gh_json(
        [
            "pr",
            "list",
            "--head",
            branch,
            "--base",
            base,
            "--state",
            "closed",
            "--limit",
            "10",
            "--json",
            "number,headRefOid,mergedAt",
        ]
    )
    if not isinstance(listed, list):
        return False
    chosen = next((pr for pr in listed if isinstance(pr, dict) and not pr.get("mergedAt")), None)
    if not chosen or not chosen.get("headRefOid"):
        return False
    for item in files:
        text = file_at_ref(item.relative, str(chosen["headRefOid"]))
        if text is None:
            return False
        try:
            if read_commit(text).lower() != item.plan.new.lower():
                return False
        except RuntimeError:
            return False
    return True


def find_open_pr(branch: str, base: str) -> dict | None:
    listed = gh_json(
        [
            "pr",
            "list",
            "--head",
            branch,
            "--base",
            base,
            "--state",
            "open",
            "--json",
            "number,url,title,headRefOid",
        ]
    )
    if not isinstance(listed, list) or not listed or not isinstance(listed[0], dict):
        return None
    return listed[0]


def recipes_base_moved(base_branch: str, head_sha: str) -> bool:
    """True when the recipes default branch has commits the open PR lacks."""
    owner, name = github_repository().split("/", 1)
    payload = gh_json(
        [
            "api",
            "graphql",
            "-f",
            "query=query($owner:String!,$name:String!,$base:String!,$head:String!){"
            "repository(owner:$owner,name:$name){ref(qualifiedName:$base){compare(headRef:$head){behindBy}}}}",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
            "-f",
            f"base=refs/heads/{base_branch}",
            "-f",
            f"head={head_sha}",
        ]
    )
    if not isinstance(payload, dict):
        raise RuntimeError("unexpected compare response")
    if payload.get("errors"):
        message = payload["errors"][0].get("message", "compare failed")
        raise RuntimeError(str(message))
    ref = payload.get("data", {}).get("repository", {}).get("ref")
    compare = None if not isinstance(ref, dict) else ref.get("compare")
    if not isinstance(compare, dict) or "behindBy" not in compare:
        raise RuntimeError("could not compare the open pull request with the base branch")
    return int(compare["behindBy"]) > 0


def choose_update(has_pr: bool, pr_pin: str | None, target: str, base_moved: bool) -> str:
    """How to keep a single open pull request current.

    open: no pull request yet.
    current: the open pull request already has this upstream commit.
    fast-forward: upstream moved and this recipes repo did not.
    rebase: the pull request was ignored while both repositories moved.
    """
    if not has_pr:
        return "open"
    if pr_pin is None:
        return "rebase"
    if pr_pin.lower() == target.lower():
        return "current"
    if base_moved:
        return "rebase"
    return "fast-forward"


def pr_body(owner: str, repo: str, files: list[FileUpdate], recipe: Path, root: Path) -> str:
    lines = [f"Updates `{recipe.relative_to(root).as_posix()}`.", ""]
    for item in files:
        plan = item.plan
        name = Path(item.relative).name
        lines.append(f"`{name}` moves from `{plan.old}` to `{plan.new}`.")
        if plan.mode == "tag":
            lines.append(
                f"The pinned commit is tag `{one_line(plan.from_tag or '')}`, and `{one_line(plan.to_tag or '')}` is the newest tag in that series."
            )
        else:
            lines.append(
                f"The pinned commit is not a tag. `{plan.upstream_branch}` now points at `{plan.new}`."
            )
        lines.append(f"Compare: https://github.com/{owner}/{repo}/compare/{plan.old}...{plan.new}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def one_line(value: str) -> str:
    cleaned = "".join(ch if ch.isprintable() else " " for ch in value)
    return " ".join(cleaned.split())


def pr_title(owner: str, repo: str, plan: Plan) -> str:
    if plan.to_tag:
        return f"update {owner}/{repo} to {one_line(plan.to_tag)}"
    return f"update {owner}/{repo} to {plan.new[:12]}"


def title_for(owner: str, repo: str, files: list[FileUpdate]) -> str:
    if len({item.plan.new.lower() for item in files}) == 1:
        return pr_title(owner, repo, files[0].plan)
    return f"update {owner}/{repo}"


def commit_message(owner: str, repo: str, files: list[FileUpdate]) -> str:
    lines = [title_for(owner, repo, files), ""]
    for item in files:
        name = Path(item.relative).name
        plan = item.plan
        if plan.mode == "tag":
            lines.append(
                f"{name}: follow tag {one_line(plan.to_tag or '')} (was {one_line(plan.from_tag or '')})."
            )
        else:
            lines.append(f"{name}: follow new commits on {plan.upstream_branch}.")
    return "\n".join(lines) + "\n"


def classify_files(branch: str, base_branch: str, files: list[FileUpdate]) -> tuple[str, dict | None]:
    existing = find_open_pr(branch, base_branch)
    if existing is None:
        return "open", None
    head = str(existing.get("headRefOid") or "")
    stale = False
    for item in files:
        text = file_at_ref(item.relative, head) if head else None
        pin = None
        if text is not None:
            try:
                pin = read_commit(text)
            except RuntimeError:
                pin = None
        if pin is None:
            return choose_update(True, None, item.plan.new, False), existing
        if pin.lower() != item.plan.new.lower():
            stale = True
    if not stale:
        return "current", existing
    moved = bool(head) and recipes_base_moved(base_branch, head)
    return choose_update(True, "stale", files[0].plan.new, moved), existing


def prepare_branch(branch: str, base_sha: str, kind: str) -> None:
    if kind == "fast-forward":
        remote_ref = f"refs/remotes/origin/{branch}"
        run(git_net("fetch", "--depth=1", "origin", f"+refs/heads/{branch}:{remote_ref}"))
        run(["git", "checkout", "-B", branch, remote_ref])
        return
    if kind == "open":
        listed = subprocess.run(
            git_net("ls-remote", "origin", f"refs/heads/{branch}"),
            text=True,
            capture_output=True,
        )
        if listed.returncode != 0:
            raise RuntimeError((listed.stderr or "ls-remote failed").strip())
        if listed.stdout.strip():
            run(git_net("push", "origin", "--delete", branch))
    run(["git", "checkout", "--force", "--detach", base_sha])
    run(["git", "checkout", "-B", branch, base_sha])


def push_branch(branch: str, base_branch: str, expected: str | None) -> None:
    if not branch.startswith("update/") or branch == base_branch:
        raise RuntimeError(f"refusing to push {branch}")
    destination = f"HEAD:refs/heads/{branch}"
    if expected:
        run(
            git_net(
                "push",
                f"--force-with-lease=refs/heads/{branch}:{expected}",
                "origin",
                destination,
            )
        )
        return
    run(git_net("push", "--set-upstream", "origin", destination))


def apply_plan(
    root: Path,
    recipe: Path,
    owner: str,
    repo: str,
    files: list[FileUpdate],
    base_branch: str,
    base_sha: str,
    kind: str,
    existing: dict | None,
) -> None:
    branch = branch_for(recipe, root)
    rebase = kind == "rebase"
    prepare_branch(branch, base_sha, kind)
    for item in files:
        path = root / item.relative
        if not path.is_file():
            run(["git", "checkout", base_sha, "--", item.relative])
        text = path.read_text()
        current = read_commit(text)
        if current.lower() == item.plan.new.lower():
            continue
        path.write_text(replace_commit(text, current, item.plan.new))
        run(["git", "add", "--", item.relative])
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if staged.returncode == 0:
        print("  no file change")
        return
    if staged.returncode != 1:
        raise RuntimeError(f"git diff exited {staged.returncode}")
    run(
        [
            "git",
            "-c",
            "user.name=github-actions[bot]",
            "-c",
            "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit",
            "-m",
            commit_message(owner, repo, files),
        ]
    )
    expected = str(existing.get("headRefOid") or "") if rebase and existing else None
    if rebase and not expected:
        raise RuntimeError("open pull request has no head commit")
    push_branch(branch, base_branch, expected or None)
    title = title_for(owner, repo, files)
    body = pr_body(owner, repo, files, recipe, root)
    if existing:
        run(["gh", "pr", "edit", str(existing["number"]), "--title", title, "--body", body])
        action = "rebased" if rebase else "updated"
        print(f"  {action} {existing['url']}")
        start_scratchpad(existing["number"], base_branch)
        return
    created = run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            base_branch,
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        ]
    )
    url = created.stdout.strip()
    print(f"  opened {url}")
    match = re.search(r"/pull/(\d+)$", url)
    if not match:
        raise RuntimeError(f"could not read pull request number from {url}")
    start_scratchpad(match.group(1), base_branch)


def start_scratchpad(number: object, base_branch: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    run(
        [
            "gh",
            "workflow",
            "run",
            "scratchpad.yml",
            "--ref",
            base_branch,
            "-f",
            f"pull_request={number}",
        ]
    )
    print(f"  started scratchpad for #{number}")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != "--dry-run"]
    if args and args[0].startswith("-"):
        raise SystemExit(f"unknown argument {args[0]}")
    recipe_filter = args[0] if args else os.environ.get("RECIPE", "")
    if not dry_run and os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("refusing to open pull requests outside GitHub Actions; use --dry-run")

    require_github_origin()
    root = Path(run(["git", "rev-parse", "--show-toplevel"]).stdout.strip())
    base_branch = os.environ.get("BASE_BRANCH") or run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    ).stdout.strip()
    if base_branch == "HEAD":
        raise SystemExit("checkout is detached; set BASE_BRANCH")
    base_sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    if not dry_run:
        dirty = run(["git", "status", "--porcelain"]).stdout.strip()
        if dirty:
            raise SystemExit("working tree is not clean")

    opened = 0
    failed: list[str] = []
    for recipe in recipe_dirs(root, recipe_filter):
        owner, repo = recipe.relative_to(root).parts[1:3]
        label = f"github.com/{owner}/{repo}"
        print(f"::group::{label}")
        try:
            files = pending_updates(owner, repo, recipe, root)
            if not files:
                continue
            branch = branch_for(recipe, root)
            kind, existing = classify_files(branch, base_branch, files)
            names = ", ".join(Path(item.relative).name for item in files)
            if kind == "current" and existing:
                print(f"  pull request {existing['url']} already has {names}")
                continue
            if kind == "open" and declined_files(branch, base_branch, files):
                print("  a closed pull request already proposed this commit")
                continue
            action = {
                "open": "open a pull request",
                "fast-forward": "update the open pull request",
                "rebase": "rebase the open pull request and force-push",
            }[kind]
            print(f"  {names}: {action}")
            if dry_run:
                opened += 1
            else:
                apply_plan(
                    root,
                    recipe,
                    owner,
                    repo,
                    files,
                    base_branch,
                    base_sha,
                    kind,
                    existing,
                )
                opened += 1
        except Exception as exc:  # noqa: BLE001 — keep going so one repo cannot block the rest
            failed.append(f"{label}: {exc}")
            print(f"::error::{label}: {exc}")
        finally:
            if not dry_run:
                subprocess.run(
                    ["git", "checkout", "--force", "--detach", base_sha],
                    check=False,
                )
            print("::endgroup::")

    verb = "would update" if dry_run else "updated"
    print(f"{opened} repositor{'y' if opened == 1 else 'ies'} {verb}")
    if failed:
        print(f"{len(failed)} failed", file=sys.stderr)
        for item in failed:
            print(item, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
