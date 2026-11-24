"""Compare the installed suite version with the public upstream version."""

import json
import re
from http.client import HTTPException
from pathlib import Path
from urllib.request import Request, urlopen

LOCAL_VERSION = Path(__file__).resolve().parents[1] / "VERSION"
UPSTREAM_VERSION = (
    "https://raw.githubusercontent.com/shoung/ProgramAnimation-skills/main/skills/program-animation/VERSION"
)


def parse_version(text):
    version = text.strip()
    if not re.fullmatch(r"(0|[1-9][0-9]{0,8})(\.(0|[1-9][0-9]{0,8})){2}", version):
        raise ValueError("Expected a version like 1.1.0")
    return tuple(map(int, version.split(".")))


def check():
    try:
        local = parse_version(LOCAL_VERSION.read_text(encoding="ascii"))
    except (OSError, ValueError):
        return {"status": "unavailable", "reason": "local_version_unreadable"}

    result = {"installed": ".".join(map(str, local))}
    try:
        request = Request(UPSTREAM_VERSION, headers={"Cache-Control": "no-cache"})
        with urlopen(request, timeout=5) as response:
            remote = parse_version(response.read(128).decode("ascii"))
    except (OSError, HTTPException, ValueError):
        return {**result, "status": "unavailable", "reason": "upstream_version_unreadable"}

    if remote > local:
        status = "update_available"
    elif remote < local:
        status = "installed_ahead"
    else:
        status = "up_to_date"
    return {**result, "upstream": ".".join(map(str, remote)), "status": status}


if __name__ == "__main__":
    print(json.dumps(check()))
