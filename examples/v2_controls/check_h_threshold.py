"""Compare the V2 cases with sound controls, using trajectory_v3_ultra.py unchanged.

The ten V2 cases are cases 1-10 of the test set in the repository root. v2_controls.txt holds
one control per case: the same user turns and first reply, and a sound second reply.
For each pair the script reads H on the last reply and reports how often the bad reply
scores below its control and how often each side falls under H < 0.3.

Run from the repository root: python examples/v2_controls/check_h_threshold.py
No model calls, no network.
"""
import csv
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENGINE = os.path.join(ROOT, "trajectory_v3_ultra.py")
TESTSET = os.path.join(ROOT, "万象渊鉴·场域诊断测试集.txt")
CONTROLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2_controls.txt")
THRESHOLD = 0.3


def last_h_per_session(path):
    """Run the engine on a test-set text file; return [(session name, H of its last turn)] in file order."""
    d = tempfile.mkdtemp()
    turns = os.path.join(d, "turns.csv")
    subprocess.run([sys.executable, "-X", "utf8", ENGINE, "--input", path, "--output_traj", os.path.join(d, "t.csv"),
                    "--output_turn", turns], capture_output=True, check=True, cwd=d)
    sessions = []                                   # a turn ending in #T01 starts a new session
    for r in csv.DictReader(open(turns, encoding="utf-8-sig")):
        if r["turn_id"].endswith("#T01") or not sessions:
            sessions.append([r["session.id"], None])
        sessions[-1][1] = float(r["H"])
    return [tuple(s) for s in sessions]


bad = last_h_per_session(TESTSET)[:10]      # cases 1-10 are the V2 set
ctl = last_h_per_session(CONTROLS)
assert len(ctl) == 10, "expected 10 controls, got %d" % len(ctl)
print("%-34s %8s %8s" % ("case", "H bad", "H ctl"))
for (sb, hb), (sc, hc) in zip(bad, ctl):
    print("%-34s %8.4f %8.4f" % (sb, hb, hc))
print("bad reply lower in H than its control: %d of 10" % sum(hb < hc for (_, hb), (_, hc) in zip(bad, ctl)))
print("H < %.1f on the bad reply:   %d of 10" % (THRESHOLD, sum(hb < THRESHOLD for _, hb in bad)))
print("H < %.1f on the control:     %d of 10" % (THRESHOLD, sum(hc < THRESHOLD for _, hc in ctl)))
