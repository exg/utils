#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import platform
import secrets
import subprocess
import sys
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import urllib3


def _get_config_dir() -> Path:
    return Path.home() / ".config" / Path(sys.argv[0]).name


def _get_open_cmd() -> str:
    if platform.system() == "Darwin":
        return "open"
    return "xdg-open"


@dataclass
class Profile:
    authorization_endpoint: str
    token_endpoint: str
    scopes: list[str]
    client_id: str
    client_secret: str
    login_hint: str | None = None
    tenant: str | None = None
    redirect_path: str = "/"
    redirect_port: int = 0


@dataclass
class Token:
    access_token: str
    expiry: int
    refresh_token: str | None


# https://developers.google.com/identity/protocols/oauth2/native-app
# https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow


class _RedirectHandler(http.server.BaseHTTPRequestHandler):
    RESPONSE = """
    <html>
      <head>
        <title>Authorization response</title>
      </head>
      <body>
        <p>Authorization completed.</p>
      </body>
    </html>
    """

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self) -> None:
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)
        if "code" in query:
            self.server.code = query["code"][0]
        self.do_HEAD()
        self.wfile.write(self.RESPONSE.encode("ascii"))


class HTTPError(Exception):
    def __init__(self, response: urllib3.response.BaseHTTPResponse):
        self.response = response


def _parse_response(resp: urllib3.response.BaseHTTPResponse) -> Token:
    if resp.status != 200:
        raise HTTPError(resp)
    data = resp.json()
    now = datetime.now(tz=timezone.utc)
    expiry = now + timedelta(seconds=int(data["expires_in"]))
    return Token(
        access_token=data["access_token"],
        expiry=int(expiry.timestamp()),
        refresh_token=data.get("refresh_token"),
    )


def _build_authorization_uri(
    profile: Profile,
    verifier: str,
    redirect_uri: str,
) -> str:
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest(),
    ).rstrip(b"=")
    params = {
        "client_id": profile.client_id,
        "scope": " ".join(profile.scopes),
        "response_type": "code",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "redirect_uri": redirect_uri,
    }
    if profile.login_hint is not None:
        params["login_hint"] = profile.login_hint
    if profile.tenant is not None:
        params["tenant"] = profile.tenant
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f"{profile.authorization_endpoint}?{query}"


class AuthError(Exception):
    pass


def _get_token(
    pool: urllib3.PoolManager,
    profile: Profile,
) -> Token:
    with http.server.HTTPServer(
        ("127.0.0.1", profile.redirect_port),
        _RedirectHandler,
    ) as httpd:
        verifier = secrets.token_urlsafe(98)
        redirect_uri = (
            f"http://localhost:{httpd.server_port}{profile.redirect_path}"
        )
        uri = _build_authorization_uri(profile, verifier, redirect_uri)
        with subprocess.Popen((_get_open_cmd(), uri)):
            try:
                httpd.code = None
                httpd.handle_request()
            except KeyboardInterrupt:
                pass
            if httpd.code is None:
                raise AuthError

            resp = pool.request(
                "POST",
                profile.token_endpoint,
                fields={
                    "client_id": profile.client_id,
                    "client_secret": profile.client_secret,
                    "scope": " ".join(profile.scopes),
                    "grant_type": "authorization_code",
                    "code": httpd.code,
                    "code_verifier": verifier,
                    "redirect_uri": redirect_uri,
                },
                encode_multipart=False,
            )
            return _parse_response(resp)


def _refresh_token(
    pool: urllib3.PoolManager,
    profile: Profile,
    token: str,
) -> Token:
    resp = pool.request(
        "POST",
        profile.token_endpoint,
        fields={
            "client_id": profile.client_id,
            "client_secret": profile.client_secret,
            "scope": " ".join(profile.scopes),
            "grant_type": "refresh_token",
            "refresh_token": token,
        },
        encode_multipart=False,
    )
    data = _parse_response(resp)
    if data.refresh_token is None:
        data.refresh_token = token
    return data


def request_authorization(
    pool: urllib3.PoolManager,
    profile: Profile,
    token: Token | None,
) -> Token:
    if token is not None and token.refresh_token is not None:
        try:
            return _refresh_token(
                pool,
                profile,
                token.refresh_token,
            )
        except HTTPError as e:
            if not (
                e.response.status == 400
                and e.response.json()["error"] == "invalid_grant"
            ):
                raise

    return _get_token(pool, profile)


def main() -> None:
    """
    Obtain an OAuth 2.0 access token.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("profile")
    args = parser.parse_args()

    with open(_get_config_dir() / "config.json", "rb") as f:
        config = json.load(f)
    if args.profile not in config:
        sys.exit(1)

    credentials_path = _get_config_dir() / "credentials.json"
    if credentials_path.exists():
        with open(credentials_path, "rb") as f:
            credentials = json.load(f)
    else:
        credentials = {}

    profile = Profile(**config[args.profile])
    if args.profile in credentials:
        token = Token(**credentials[args.profile])
    else:
        token = None

    now = datetime.now(tz=timezone.utc)
    if (
        token is None
        or datetime.fromtimestamp(token.expiry, tz=timezone.utc) <= now
    ):
        pool = urllib3.PoolManager()
        token = request_authorization(pool, profile, token)
        credentials[args.profile] = asdict(token)
        credentials_path.touch(mode=0o600)
        with open(credentials_path, "w", encoding="utf-8") as f:
            json.dump(credentials, f, indent=2)

    print(token.access_token)


if __name__ == "__main__":
    main()
