"""udah-scorer: U/D/A/H scores for multi-turn conversations.

The scoring core is `trajectory_v3_ultra.py`, shipped byte-identical to the copy at the root of
https://github.com/luoxuejian000/traceai-udah-scorer-poc. This package only wraps it: a command line,
a traceAI adapter, and tests. `CORE_SHA256` is the hash the tests hold the core to.
"""
from . import trajectory_v3_ultra as core
from .trajectory_v3_ultra import compute_a, compute_d, compute_h, compute_u, score_text

__version__ = "0.1.0"
CORE_SHA256 = "37a2c0318679136a278a040406a13df771a514dfaf263e19005bd58fd51e2679"

__all__ = ["core", "score_text", "compute_u", "compute_d", "compute_a", "compute_h",
           "CORE_SHA256", "core_sha256", "__version__"]


def core_sha256() -> str:
    """sha256 of the installed core, line endings normalised to LF (git stores it that way)."""
    import hashlib
    import os
    with open(os.path.join(os.path.dirname(__file__), "trajectory_v3_ultra.py"), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
