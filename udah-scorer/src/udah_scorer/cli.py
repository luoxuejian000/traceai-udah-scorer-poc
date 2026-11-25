"""Command line for udah-scorer.

    udah text "some reply"              U, D, A, H of one text
    udah cases --input cases.json       the core's own case runner, unchanged
    udah traceai trace.json --out x.csv score a traceAI export, each turn once
    udah verify-core                    check the installed core against CORE_SHA256
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import CORE_SHA256, __version__, core, core_sha256, traceai


def _text(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="udah text", description="U, D, A, H of one text")
    ap.add_argument("text", help="the text to score; '-' reads standard input")
    ap.add_argument("--top-terms", type=int, default=core.DEFAULT_TOP_TERMS)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.text == "-" else a.text
    u, d, adv, h = core.score_text(text, top_terms=a.top_terms)
    print(json.dumps({"U": u, "D": d, "A": adv, "H": h}))
    return 0


def _verify(argv: List[str]) -> int:
    argparse.ArgumentParser(prog="udah verify-core").parse_args(argv)
    got = core_sha256()
    ok = got == CORE_SHA256
    print(("OK" if ok else "MISMATCH") + " core sha256 " + got)
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"text": _text, "cases": core.main, "traceai": traceai.main, "verify-core": _verify}
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if argv[0] == "--version":
        print("udah-scorer " + __version__)
        return 0
    if argv[0] not in commands:
        print("unknown command: %s\n\n%s" % (argv[0], __doc__.strip()), file=sys.stderr)
        return 2
    return int(commands[argv[0]](argv[1:]) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
