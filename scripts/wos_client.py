"""WoS Starter transport for Actions and local Keychain-backed refreshes."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request


ENDPOINT = "https://api.clarivate.com/apis/wos-starter/v2/documents"
CONFIG = Path.home() / ".config" / "wos" / "config.json"


def credential():
    key = os.environ.get("WOS_API_KEY", "").strip()
    if key:
        return key
    if not CONFIG.exists():
        raise RuntimeError("WOS_API_KEY is not configured; previous WoS data preserved")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    result = subprocess.run(
        ["security", "find-generic-password", "-s", config["keychain_service"],
         "-a", config["keychain_account"], "-w"],
        capture_output=True, text=True, timeout=20,
    )
    if result.returncode or not result.stdout.strip():
        raise RuntimeError("WoS credential is unavailable in the local Keychain")
    return result.stdout.strip()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def query_documents(query, limit=50, page=1):
    key = credential()
    params = urllib.parse.urlencode({"db": "WOS", "q": query, "limit": limit, "page": page})
    request = urllib.request.Request(
        ENDPOINT + "?" + params,
        headers={"X-ApiKey": key, "Accept": "application/json", "User-Agent": "xy-lilab-citations/1.0"},
    )
    opener = urllib.request.build_opener(NoRedirect)
    for attempt in range(3):
        try:
            with opener.open(request, timeout=30) as response:
                data = json.load(response)
            if not isinstance(data, dict) or "metadata" not in data or "hits" not in data:
                raise RuntimeError("Unexpected WoS response; previous data preserved")
            data["_request"] = {"database": "WOS", "query": query,
                                "retrieved_at": datetime.now(timezone.utc).isoformat()}
            return data
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                retry = error.headers.get("Retry-After", "")
                time.sleep(min(int(retry), 30) if retry.isdigit() else 2 ** (attempt + 1))
                continue
            # Do not print response bodies: an upstream error could echo headers.
            raise RuntimeError(f"WoS returned HTTP {error.code}; previous data preserved") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError("WoS connection failed; previous data preserved") from None
