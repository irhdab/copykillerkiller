#!/usr/bin/env python3
"""Report what this environment can do before a review task starts."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCHEMA_VERSION = 1
TIERS = ("full", "reduced", "manual")

NEXT_STEP = {
    "full": "prepare_review.py와 create_review_copy.py를 그대로 실행한다.",
    "reduced": "PDF에서 텍스트를 스크립트로 뽑을 수 없다. 배치 텍스트를 직접 만들어 .txt로 넘기거나 대조 엔진만 사용한다.",
    "manual": "스크립트를 실행할 수 없다. 사용자에게 명령과 입력을 안내하고 돌려받은 JSON으로 검토를 이어간다.",
}


def check_python():
    version = "%d.%d.%d" % sys.version_info[:3]
    ok = sys.version_info >= (3, 9)
    return {"ok": ok, "version": version, "path": sys.executable}


def check_pdftotext():
    binary = shutil.which("pdftotext")
    if not binary:
        return {"ok": False, "path": None, "version": None}
    try:
        result = subprocess.run(
            [binary, "-v"], capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.SubprocessError):
        return {"ok": True, "path": binary, "version": None}
    banner = (result.stderr or result.stdout or "").strip().splitlines()
    return {"ok": True, "path": binary, "version": banner[0] if banner else None}


def check_temp_write():
    try:
        with tempfile.TemporaryDirectory(prefix="capability-") as folder:
            probe = Path(folder) / "probe.txt"
            probe.write_text("ok", encoding="utf-8")
            readable = probe.read_text(encoding="utf-8") == "ok"
    except OSError as exc:
        return {"ok": False, "dir": tempfile.gettempdir(), "error": type(exc).__name__}
    return {"ok": readable, "dir": tempfile.gettempdir(), "error": None}


def assess():
    python = check_python()
    pdftotext = check_pdftotext()
    temp = check_temp_write()
    if not python["ok"] or not temp["ok"]:
        tier = "manual"
    elif not pdftotext["ok"]:
        tier = "reduced"
    else:
        tier = "full"
    return {
        "schema_version": SCHEMA_VERSION,
        "tier": tier,
        "checks": {"python": python, "pdftotext": pdftotext, "temp_write": temp},
        "docx_comment_copy": python["ok"] and temp["ok"],
        "next_step": NEXT_STEP[tier],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tier-only",
        action="store_true",
        help="print only the tier name for shell use",
    )
    args = parser.parse_args()
    result = assess()
    if args.tier_only:
        print(result["tier"])
        return
    sys.stdout.buffer.write(
        (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )


if __name__ == "__main__":
    main()
