#!/usr/bin/env python3
"""Render the VizAdvisor Quarto site and publish a NEW Posit Connect Cloud content instance.

Hard rule: never overwrite the PSYCH 755 content id
  019f9a10-ebb9-d1d5-839f-97e794bfd0ca

Creates a fresh content record under the jackjburleson account, uploads _site/,
publishes, writes _publish.yml, and verifies the public share URL.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_NAME = "jackjburleson"
FORBIDDEN_CONTENT_ID = "019f9a10-ebb9-d1d5-839f-97e794bfd0ca"
API = "https://api.connect.posit.cloud/v1"
AUTH_HOST = "login.posit.cloud"
CLIENT_ID = "quarto-cli"
SCOPE = "vivid"


def _log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str], *, cwd: Path = ROOT) -> None:
    _log("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_quarto() -> None:
    if shutil.which("quarto") is None:
        raise SystemExit("quarto not on PATH; install Quarto ≥ 1.10")
    out = subprocess.check_output(["quarto", "--version"], text=True).strip()
    _log(f"quarto {out}")


def render_site() -> Path:
    ensure_quarto()
    run(["quarto", "render"])
    site = ROOT / "_site"
    if not (site / "index.html").is_file():
        raise SystemExit("quarto render did not produce _site/index.html")
    return site


def post_form(url: str, data: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def device_auth() -> dict:
    auth = post_form(
        f"https://{AUTH_HOST}/oauth/device/authorize",
        {"scope": SCOPE, "client_id": CLIENT_ID},
    )
    _log("=" * 72)
    _log("AUTHORIZE NOW (Posit Connect Cloud / JackJBurleson)")
    _log("=" * 72)
    _log(f"URL:  {auth['verification_uri_complete']}")
    _log(f"CODE: {auth['user_code']}")
    _log("=" * 72)
    interval = max(int(auth.get("interval", 5)), 5)
    expires = int(auth.get("expires_in", 1800))
    start = time.time()
    while True:
        if time.time() - start > expires:
            raise SystemExit("Device authorization timed out.")
        try:
            tok = post_form(
                f"https://{AUTH_HOST}/oauth/token",
                {
                    "scope": SCOPE,
                    "client_id": CLIENT_ID,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": auth["device_code"],
                },
            )
            _log(f"Authorized after {time.time() - start:.0f}s")
            return tok
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                code = json.loads(raw).get("error", raw)
            except Exception:
                code = raw.strip()
            if code == "authorization_pending":
                time.sleep(interval)
                continue
            if code == "slow_down":
                interval += 5
                time.sleep(interval)
                continue
            raise SystemExit(f"OAuth error: {code}")


def load_tokens() -> str:
    access = os.environ.get("POSIT_CONNECT_CLOUD_ACCESS_TOKEN")
    if access:
        _log("Using POSIT_CONNECT_CLOUD_ACCESS_TOKEN from environment")
        return access
    cached = Path("/tmp/posit-tokens.json")
    if cached.is_file():
        tok = json.loads(cached.read_text(encoding="utf-8"))
        if tok.get("access_token") and not tok.get("error"):
            _log("Using cached tokens from /tmp/posit-tokens.json")
            return tok["access_token"]
    tok = device_auth()
    Path("/tmp/posit-tokens.json").write_text(json.dumps(tok, indent=2), encoding="utf-8")
    return tok["access_token"]


def api(
    method: str,
    path: str,
    access: str,
    body: dict | None = None,
) -> dict | None:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{API}/{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw.decode()) if raw else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} → {e.code}: {e.read().decode()[:1200]}") from e


def assert_writable_account(access: str) -> str:
    env_id = os.environ.get("POSIT_CONNECT_CLOUD_ACCOUNT_ID")
    accounts = api("GET", "accounts?has_user_role=true", access) or {}
    rows = accounts.get("data") or []
    names = [a.get("name") for a in rows]
    _log(f"Authorized accounts: {names}")
    for a in rows:
        if a.get("name") == ACCOUNT_NAME:
            return a["id"]
    if env_id:
        return env_id
    if not rows:
        raise SystemExit("No publishable Posit accounts for this login.")
    _log(f"WARNING: '{ACCOUNT_NAME}' not in account list; using {rows[0].get('name')}")
    return rows[0]["id"]


def make_bundle(site: Path) -> bytes:
    buf = io.BytesIO()
    files = sorted(p for p in site.rglob("*") if p.is_file())
    manifest = {
        "version": 1,
        "locale": "en_US",
        "platform": "4.0.0",
        "metadata": {"appmode": "static", "primary_rmd": None, "primary_html": "index.html"},
        "packages": None,
        "files": {p.relative_to(site).as_posix(): {"checksum": ""} for p in files},
        "users": None,
    }
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        man = json.dumps(manifest).encode()
        info = tarfile.TarInfo("manifest.json")
        info.size = len(man)
        tar.addfile(info, io.BytesIO(man))
        for p in files:
            tar.add(p, arcname=p.relative_to(site).as_posix())
    return buf.getvalue()


def create_content(access: str, account_id: str, *, title: str, name: str) -> dict:
    """Create a brand-new content instance (never reuse FORBIDDEN_CONTENT_ID)."""
    body = {
        "account_id": account_id,
        "title": title,
        "description": "SME data visualization consultant — Quarto documentation site",
        "access": "public",
        "next_revision": {
            "source_type": "bundle",
            "primary_file": "index.html",
            "app_mode": "static",
            "content_type": "static",
        },
    }
    created = api("POST", "contents", access, body)
    if not created or not created.get("id"):
        raise SystemExit(f"Failed to create content: {created}")
    content_id = created["id"]
    if content_id == FORBIDDEN_CONTENT_ID:
        raise SystemExit("Refusing to use forbidden PSYCH 755 content id")
    _log(f"Created NEW content id={content_id} (name hint={name})")
    return created


def publish_to_content(access: str, content_id: str, site: Path) -> dict:
    if content_id == FORBIDDEN_CONTENT_ID:
        raise SystemExit("Refusing to overwrite PSYCH 755 content")

    updated = api(
        "PATCH",
        f"contents/{content_id}?new_bundle=true",
        access,
        {
            "secrets": [],
            "revision_overrides": {"primary_file": "index.html", "app_mode": "static"},
        },
    ) or {}
    rev = updated.get("next_revision") or updated.get("current_revision") or {}
    upload_url = rev.get("source_bundle_upload_url")
    if not upload_url:
        raise SystemExit(f"No upload URL for content {content_id}: {updated}")

    bundle = make_bundle(site)
    _log(f"Uploading bundle ({len(bundle)} bytes)")
    req = urllib.request.Request(
        upload_url,
        data=bundle,
        method="POST",
        headers={"Content-Type": "application/gzip"},
    )
    with urllib.request.urlopen(req) as r:
        _log(f"upload_status {r.status}")

    req = urllib.request.Request(
        f"{API}/contents/{content_id}/publish",
        method="POST",
        headers={"Accept": "application/json", "Authorization": f"Bearer {access}"},
    )
    with urllib.request.urlopen(req) as r:
        _log(f"publish_http {r.status}")
        r.read()

    share_url = f"https://{content_id}.share.connect.posit.cloud/"
    ui_url = f"https://connect.posit.cloud/{ACCOUNT_NAME}/content/{content_id}"

    for i in range(60):
        content = api("GET", f"contents/{content_id}", access) or {}
        rev = content.get("current_revision") or {}
        result = rev.get("publish_result")
        status = rev.get("status") or rev.get("state")
        url = rev.get("url") or content.get("share_url") or share_url
        _log(f"poll[{i}] status={status} result={result} url={url}")
        if result == "success" or status == "published":
            return {"content": content, "share_url": url, "ui_url": ui_url, "content_id": content_id}
        if result and result not in {"success", "running", None}:
            raise SystemExit(
                f"Publish failed: {rev.get('publish_error_code')} {rev.get('publish_error_args')}"
            )
        time.sleep(3)
    raise SystemExit("Timed out waiting for publish success")


def write_publish_yml(content_id: str, ui_url: str) -> None:
    # Use dashboard-style URL like the psych755 example
    text = (
        "- source: project\n"
        "  posit-connect-cloud:\n"
        f"    - id: {content_id}\n"
        f"      url: {ui_url}\n"
    )
    path = ROOT / "_publish.yml"
    path.write_text(text, encoding="utf-8")
    _log(f"Wrote {path}")


def verify_live(share_url: str, *, expect_substrings: list[str]) -> None:
    req = urllib.request.Request(share_url, headers={"User-Agent": "vizadvisor-posit-publish/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
        code = r.status
    if code != 200:
        raise SystemExit(f"Live verify HTTP {code}")
    missing = [s for s in expect_substrings if s not in html]
    if missing:
        raise SystemExit(f"Live page missing expected strings: {missing}")
    _log(f"Live verification OK ({len(html)} bytes): {share_url}")
    try:
        from playwright.sync_api import sync_playwright

        art = Path("/opt/cursor/artifacts")
        art.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(share_url, wait_until="networkidle", timeout=90000)
            page.screenshot(path=str(art / "vizadvisor-connect-cloud.png"), full_page=False)
            browser.close()
        _log(f"Screenshot → {art / 'vizadvisor-connect-cloud.png'}")
    except Exception as exc:  # noqa: BLE001
        _log(f"Screenshot skipped: {exc}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-render", action="store_true")
    p.add_argument("--title", default="VizAdvisor")
    p.add_argument("--name", default="vizadvisor")
    p.add_argument(
        "--content-id",
        default="",
        help="Publish to an already-created NEW content id (must not be the PSYCH 755 id)",
    )
    p.add_argument(
        "--expect",
        action="append",
        default=[],
        help="Substring that must appear on the live share page",
    )
    args = p.parse_args(argv)

    # Safety: if an existing _publish.yml points at the forbidden id, refuse.
    pub = ROOT / "_publish.yml"
    if pub.is_file() and FORBIDDEN_CONTENT_ID in pub.read_text(encoding="utf-8"):
        raise SystemExit(
            "_publish.yml points at the PSYCH 755 content id — refusing. "
            "Remove it to create a new VizAdvisor content instance."
        )

    if not args.skip_render:
        site = render_site()
    else:
        site = ROOT / "_site"
        if not (site / "index.html").is_file():
            raise SystemExit("_site/index.html missing")

    access = load_tokens()
    account_id = assert_writable_account(access)
    _log(f"Using account_id={account_id}")

    if args.content_id:
        content_id = args.content_id.strip()
        if content_id == FORBIDDEN_CONTENT_ID:
            raise SystemExit("Refusing to overwrite PSYCH 755 content")
        _log(f"Using existing NEW content id={content_id}")
    else:
        created = create_content(access, account_id, title=args.title, name=args.name)
        content_id = created["id"]
    result = publish_to_content(access, content_id, site)
    write_publish_yml(content_id, result["ui_url"])

    # Update site-url in _quarto.yml for future renders (best-effort)
    qyml = ROOT / "_quarto.yml"
    text = qyml.read_text(encoding="utf-8")
    marker = "  description:"
    if "site-url:" not in text:
        text = text.replace(
            marker,
            f"  site-url: {result['ui_url']}\n{marker}",
            1,
        )
        qyml.write_text(text, encoding="utf-8")
        _log("Inserted website.site-url into _quarto.yml")

    expect = list(args.expect) or ["VizAdvisor", "subject-matter-expert", "Get Started"]
    verify_live(result["share_url"], expect_substrings=expect)

    out = {
        **result,
        "account": ACCOUNT_NAME,
        "forbidden_content_id": FORBIDDEN_CONTENT_ID,
    }
    Path("/tmp/posit-publish-result.json").write_text(json.dumps(out, indent=2, default=str))
    _log("UI_URL " + result["ui_url"])
    _log("SHARE_URL " + result["share_url"])
    _log("CONTENT_ID " + content_id)
    _log("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
