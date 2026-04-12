import base64
import json
import os
from typing import Any
from urllib import error, parse, request


class GitHubSyncError(RuntimeError):
    pass


def _maybe_streamlit_secret(name: str) -> str | None:
    try:
        import streamlit as st
    except ImportError:
        return None

    if name in st.secrets:
        value = st.secrets[name]
        return str(value) if value is not None else None
    return None


def _get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    secret_value = _maybe_streamlit_secret(name)
    if secret_value:
        return secret_value
    return default


def is_enabled() -> bool:
    return bool(_get_setting("GITHUB_TOKEN") and _get_setting("GITHUB_REPO"))


def _api_request(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = _get_setting("GITHUB_TOKEN")
    if not token:
        raise GitHubSyncError("Missing GitHub token. Set GITHUB_TOKEN in the environment or Streamlit secrets.")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        details = raw
        try:
            parsed = json.loads(raw)
            details = parsed.get("message", parsed)
        except json.JSONDecodeError:
            pass
        raise GitHubSyncError(f"GitHub API request failed ({exc.code} {exc.reason}): {details}") from exc

    return json.loads(raw) if raw else {}


def _contents_url(repo_path: str) -> str:
    repo = _get_setting("GITHUB_REPO")
    branch = _get_setting("GITHUB_BRANCH", "main")
    if not repo:
        raise GitHubSyncError("Missing GITHUB_REPO. Expected format owner/repo.")
    quoted_repo = parse.quote(repo, safe="/")
    quoted_path = parse.quote(repo_path.lstrip("/"), safe="/")
    return f"https://api.github.com/repos/{quoted_repo}/contents/{quoted_path}?ref={parse.quote(branch)}"


def _get_file_state(repo_path: str) -> tuple[dict[str, Any], str]:
    payload = _api_request("GET", _contents_url(repo_path))
    content = payload.get("content", "")
    sha = payload.get("sha")
    if not sha:
        raise GitHubSyncError(f"GitHub did not return a blob SHA for {repo_path}.")
    decoded = base64.b64decode(content).decode("utf-8") if content else "{}"
    try:
        parsed = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise GitHubSyncError(f"{repo_path} on GitHub is not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise GitHubSyncError(f"{repo_path} on GitHub must be a JSON object.")
    return parsed, sha


def update_json_entry(repo_path: str, key: str, value: Any, commit_message: str, max_attempts: int = 3) -> None:
    repo = _get_setting("GITHUB_REPO")
    branch = _get_setting("GITHUB_BRANCH", "main")
    if not repo:
        raise GitHubSyncError("Missing GITHUB_REPO. Expected format owner/repo.")

    url = f"https://api.github.com/repos/{parse.quote(repo, safe='/')}/contents/{parse.quote(repo_path.lstrip('/'), safe='/')}"
    last_error: GitHubSyncError | None = None

    for _ in range(max_attempts):
        current_data, sha = _get_file_state(repo_path)
        current_data[key] = value
        encoded_content = base64.b64encode(
            (json.dumps(current_data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        ).decode("utf-8")
        payload = {
            "message": commit_message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch,
        }
        try:
            _api_request("PUT", url, payload)
            return
        except GitHubSyncError as exc:
            last_error = exc
            if "409" not in str(exc) and "422" not in str(exc):
                break

    if last_error:
        raise last_error

