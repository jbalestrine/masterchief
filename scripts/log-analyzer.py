#!/usr/bin/env python3
"""MasterChief - Log Analyzer"""
import re, sys, os
from collections import Counter, defaultdict
from pathlib import Path

def analyze_log(filepath):
    print(f"[MasterChief] Log Analyzer: {filepath}")
    print("=" * 50)
    levels = Counter()
    hourly = defaultdict(int)
    errors = []
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}):\d{2}.*?(DEBUG|INFO|WARNING|ERROR|CRITICAL)')

    with open(filepath, 'r', errors='ignore') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                hour, level = m.groups()
                levels[level] += 1
                hourly[hour] += 1
                if level in ('ERROR', 'CRITICAL'):
                    errors.append(line.strip()[:120])

    total = sum(levels.values())
    print(f"  Total entries: {total}")
    for lvl in ('DEBUG','INFO','WARNING','ERROR','CRITICAL'):
        if levels[lvl]:
            print(f"  {lvl:10s}: {levels[lvl]:>6d} ({levels[lvl]/total*100:.1f}%)")

    if errors:
        print(f"\n  Recent errors ({len(errors)} total):")
        for e in errors[-5:]:
            print(f"    {e}")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'app.log'
    if os.path.exists(path):
        analyze_log(path)
    else:
        print(f"Log file not found: {path}")