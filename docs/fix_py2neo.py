"""
Custom script to fix a bug in py2neo library.
See [Issue 942](https://github.com/py2neo-org/py2neo/issues/942).
"""

import argparse
from pathlib import Path


OLD = "if self.graph and self.identity"
NEW = "if self.graph and self.identity is not None"
FILEPATH = Path("site-packages") / "py2neo" / "data.py"


parser = argparse.ArgumentParser(description="Fix bug in py2neo.")
parser.add_argument(
    "pythondir",
    type=Path,
    help="relative path to python directory in virtual environment",
)
args = parser.parse_args()
path: Path = args.pythondir / FILEPATH

print("Fixing py2neo bug...")
print(path)

with path.open("r") as f:
    filedata = f.read()
print("Old:", len(filedata))

filedata = filedata.replace(OLD, NEW, 1)

with path.open("w") as f:
    size = f.write(filedata)
print("Written:", size)
