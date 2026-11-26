"""Tests for udah-scorer. Run from udah-scorer/: python -m unittest discover -s tests

They hold the package to three things:
  1. the core is byte-identical to the pinned hash (and to the repository root copy when present);
  2. the wrapper changes no score: the V2-06 example reproduces H 0.5759 -> 0.1559, and the
     traceAI adapter gives the same numbers as the core run on the same conversation as text;
  3. the adapter counts each turn once, and the command line works when installed.
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest

import udah_scorer as P
from udah_scorer import core, traceai as T

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
REPO_ROOT_CORE = os.path.normpath(os.path.join(HERE, "..", "..", "trajectory_v3_ultra.py"))


def m(role, text):
    return {"role": role, "content": text}


def span(sid, n, inp, out, **usage):
    attrs = {"session.id": sid, "gen_ai.input.messages": inp, "gen_ai.output.messages": out}
    attrs.update({"gen_ai.usage." + k: v for k, v in usage.items()})
    return {"spanId": "%s-%d" % (sid, n), "traceId": "t-" + sid, "startTimeUnixNano": n, "attributes": attrs}


def rows_for(spans):
    return T.score_sessions(T.build_sessions(T.load_spans(json.dumps(spans, ensure_ascii=False))))


def rows_for_file(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return T.score_sessions(T.build_sessions(T.load_spans(f.read())))


def udah(*args, cwd=None):
    return subprocess.run([sys.executable, "-X", "utf8", "-m", "udah_scorer.cli", *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=cwd)


class CoreIsUnchanged(unittest.TestCase):
    def test_core_matches_pinned_hash(self):
        self.assertEqual(P.core_sha256(), P.CORE_SHA256)

    @unittest.skipUnless(os.path.isfile(REPO_ROOT_CORE), "not inside the repository checkout")
    def test_core_matches_repository_root_copy(self):
        def norm(p):
            with open(p, "rb") as f:
                return f.read().replace(b"\r\n", b"\n")
        self.assertEqual(norm(core.__file__), norm(REPO_ROOT_CORE))

    def test_hash_check_can_fail(self):
        """Control: a one-byte change to a copy of the core must change the hash."""
        with open(core.__file__, "rb") as f:
            raw = f.read().replace(b"\r\n", b"\n")
        import hashlib
        self.assertNotEqual(hashlib.sha256(raw + b" ").hexdigest(), P.CORE_SHA256)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), P.CORE_SHA256)


class ScoresAreUnchanged(unittest.TestCase):
    def test_v2_06_circular_logic(self):
        rows = rows_for_file("v2_06_circular_logic.json")
        self.assertEqual([(r["U"], r["D"], r["A"], r["H"]) for r in rows],
                         [(1.0, 0.4397, 0.0, 0.5759), (0.3449, 0.0447, 0.0, 0.1559)])

    def test_v2_06_control(self):
        rows = rows_for_file("v2_06_control.json")
        self.assertEqual([(r["U"], r["D"], r["A"], r["H"]) for r in rows],
                         [(1.0, 0.4397, 0.0, 0.5759), (1.0, 0.2406, 0.0, 0.4962)])

    def test_adapter_equals_core_on_text(self):
        """The adapter adds no scoring of its own: same conversation as text through the core's runner."""
        turns = []
        for r in rows_for_file("v2_06_circular_logic.json"):
            turns.append((json.loads(r["gen_ai.input.messages"])[0]["content"], json.loads(r["gen_ai.output.messages"])[0]["content"]))
        text = "Case 6 (Circular Logic)\n" + "".join("User: %s\nAI: %s\n" % t for t in turns)
        d = tempfile.mkdtemp()
        src = os.path.join(d, "case6.txt")
        with open(src, "w", encoding="utf-8") as f:
            f.write(text)
        out = udah("cases", "--input", src, "--output_traj", os.path.join(d, "t.csv"),
                   "--output_turn", os.path.join(d, "turns.csv"), cwd=d)
        self.assertEqual(out.returncode, 0, out.stderr)
        with open(os.path.join(d, "turns.csv"), encoding="utf-8-sig") as f:
            core_h = [float(r["H"]) for r in csv.DictReader(f)]
        self.assertEqual(core_h, [0.5759, 0.1559])

    def test_score_text_matches_core(self):
        t = "Rayleigh scattering: shorter wavelengths scatter more in the atmosphere."
        self.assertEqual(P.score_text(t), core.score_text(t))


class EachTurnOnce(unittest.TestCase):
    def test_history_is_scored_once(self):
        spans = [span("s", 1, [m("user", "Q1")], [m("assistant", "A1 answer text")]),
                 span("s", 2, [m("user", "Q1"), m("assistant", "A1 answer text"), m("user", "Q2")], [m("assistant", "A2 answer text")])]
        rows = rows_for(spans)
        self.assertEqual([json.loads(r["gen_ai.input.messages"]) for r in rows], [[m("user", "Q1")], [m("user", "Q2")]])

    def test_reply_without_new_input_is_scored(self):
        spans = [span("s", 1, [m("user", "Q")], [m("assistant", "first answer")]),
                 span("s", 2, [m("user", "Q"), m("assistant", "first answer")], [m("assistant", "second answer")])]
        self.assertEqual(len(rows_for(spans)), 2)

    def test_same_reply_exported_twice_counts_once(self):
        s = span("s", 1, [m("user", "Q")], [m("assistant", "answer")])
        self.assertEqual(len(rows_for([s, dict(s, spanId="dup", startTimeUnixNano=2)])), 1)

    def test_usage_is_copied(self):
        rows = rows_for([span("a", 1, [m("user", "Qa")], [m("assistant", "Aa")], input_tokens=10, output_tokens=5)])
        self.assertEqual((rows[0]["gen_ai.usage.input_tokens"], rows[0]["gen_ai.usage.total_tokens"]), (10, 15))


class CommandLine(unittest.TestCase):
    def test_verify_core(self):
        out = udah("verify-core")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("OK", out.stdout)

    def test_text(self):
        out = udah("text", "Rayleigh scattering: shorter wavelengths scatter more.")
        self.assertEqual(sorted(json.loads(out.stdout)), ["A", "D", "H", "U"])

    def test_traceai_writes_columns(self):
        d = tempfile.mkdtemp()
        o = os.path.join(d, "o.csv")
        out = udah("traceai", os.path.join(DATA, "v2_06_circular_logic.json"), "--out", o)
        self.assertEqual(out.returncode, 0, out.stderr)
        with open(o, encoding="utf-8-sig") as f:
            self.assertEqual(next(csv.reader(f)), T.COLUMNS)

    def test_unknown_command(self):
        self.assertEqual(udah("nope").returncode, 2)


if __name__ == "__main__":
    unittest.main()
