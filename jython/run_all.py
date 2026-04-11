# -*- coding: utf-8 -*-
"""
run_all.py
==========
Runs every demo file in sequence.
Outputs a clear header for each, captures any errors, and prints a summary.

Usage:  jython run_all.py
"""

import sys
import traceback
from java.lang import System

DEMOS = [
    ("01_control_flow.py",       "Control Flow"),
    ("02_iteration.py",          "Iteration"),
    ("03_data_types.py",         "Data Types & Access"),
    ("04_subroutines.py",        "Subroutines & Functions"),
    ("05_control_abstraction.py","Control Abstraction"),
    ("06_data_abstraction.py",   "Data Abstraction"),
    ("07_oop.py",                "Object-Oriented Programming"),
]

WIDTH = 60

def banner(title):
    print("\n" + "=" * WIDTH)
    line = "  DEMO: " + title
    print(line)
    print("=" * WIDTH)

def run_file(filename):
    """Execute a demo file in the current global namespace."""
    f = open(filename, "r")
    try:
        source = f.read()
    finally:
        f.close()
    code = compile(source, filename, "exec")
    exec(code, {"__name__": "__main__", "__file__": filename})

passed = []
failed = []

start_ms = System.currentTimeMillis()

for filename, title in DEMOS:
    banner(title)
    try:
        run_file(filename)
        passed.append(title)
    except Exception as e:
        print("\n  *** ERROR in {} ***".format(filename))
        traceback.print_exc()
        failed.append((title, str(e)))

elapsed = (System.currentTimeMillis() - start_ms) / 1000.0

# ── Summary ──────────────────────────────────────────
print("\n" + "=" * WIDTH)
print("  SUMMARY  ({:.2f}s)".format(elapsed))
print("=" * WIDTH)
print("  Passed: {}".format(len(passed)))
for t in passed:
    print("    [OK]   " + t)

if failed:
    print("  Failed: {}".format(len(failed)))
    for t, err in failed:
        print("    [FAIL] {} - {}".format(t, err))
else:
    print("\n  All demos ran successfully!")
print("=" * WIDTH + "\n")
