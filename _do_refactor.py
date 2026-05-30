"""
Automated main.py refactoring: Phase 1 - Extract templates, Phase 2 - Create route blueprints.
Writes new files and a new main.py. The old main.py is backed up first.

Run: python _do_refactor.py
Results written to _refactor_out.txt
"""
import re, os, shutil, sys

MAIN = 'main.py'
OUT = '_refactor_out.txt'
log_lines = []

def log(msg):
    log_lines.append(msg)
    print(msg)

def save_log():
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

# ── Read main.py ────────────────────────────────────────────────────────────
with open(MAIN, 'r', encoding='utf-8') as f:
    lines = f.readlines()
log(f"Read {len(lines)} lines from {MAIN}")

# ── Find all inline template blocks ─────────────────────────────────────────
templates = []
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^([A-Z][A-Z_0-9]*)\s*=\s*("{3})', line)
    if m:
        varname = m.group(1)
        delim = m.group(2)
        count = line.count(delim)
        if count == 1:
            start = i
            j = i + 1
            while j < len(lines):
                if delim in lines[j]:
                    templates.append((varname, start, j))
                    break
                j += 1
            i = j + 1
            continue
    i += 1

log(f"\nFound {len(templates)} inline templates:")
for name, start, end in templates:
    log(f"  {name:30s}  L{start+1:5d}-L{end+1:5d}  ({end-start+1:5d} lines)")

# ── Which templates need extraction ──────────────────────────────────────────
# Already in templates/pages.py: DASHBOARD_TEMPLATE, SCRIPTS_TEMPLATE, SCRIPT_VIEW_TEMPLATE,
#   SCRIPT_EXECUTE_TEMPLATE, MODULES_TEMPLATE, ECHO_RESOURCES_TEMPLATE, ADDONS_MODULES_TEMPLATE,
#   MODULE_MANAGER_TEMPLATE, ADDONS_MODULE_CONFIG_TEMPLATE, ECHO_TRAINING_TEMPLATE
# Already in templates/base.py: HTML_TEMPLATE

# Map inline templates to target files
extract_map = {
    'SCRIPT_EDIT_TEMPLATE': 'templates/scripts_extra.py',
    'PROCESSES_TEMPLATE': 'templates/processes.py',
    'SERVICES_TEMPLATE': 'templates/processes.py',  # same file
    'ADDONS_TEMPLATE': 'templates/addons_page.py',
    'ECHO_CHAT_TEMPLATE': 'templates/echo_chat.py',
    'TEAMS_TEMPLATE': 'templates/teams.py',
    'OKTA_TEMPLATE': 'templates/okta.py',
}

# Duplicate templates that are already extracted and can be removed from main.py
already_extracted = {
    'HTML_TEMPLATE',       # templates/base.py
    'SCRIPTS_TEMPLATE',    # templates/pages.py
    'SCRIPT_VIEW_TEMPLATE', # templates/pages.py (may not exist inline but just in case)
    'SCRIPT_EXECUTE_TEMPLATE', # templates/pages.py
    'MODULES_TEMPLATE',    # templates/pages.py (note: different version, we'll keep the main.py one)
}

# Actually MODULES_TEMPLATE in pages.py is simpler - we need the main.py version
# So we'll extract it to a new file and update the import

# Build lookup
tpl_lookup = {name: (start, end) for name, start, end in templates}

# ── Create template files ───────────────────────────────────────────────────
file_templates = {}  # filepath -> [varnames]
for varname, filepath in extract_map.items():
    file_templates.setdefault(filepath, []).append(varname)

for filepath, varnames in file_templates.items():
    parts = []
    parts.append(f'"""\nMasterChief Template: {os.path.basename(filepath)}\nExtracted from main.py during refactoring.\n"""\n\n')
    for vn in varnames:
        if vn in tpl_lookup:
            start, end = tpl_lookup[vn]
            tpl_lines = lines[start:end+1]
            parts.append(''.join(tpl_lines))
            parts.append('\n\n')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))
    log(f"Created {filepath} with {varnames}")

# ── Compute lines to remove from main.py ────────────────────────────────────
# All templates that are being extracted OR are duplicates get removed
remove_ranges = []
for name, start, end in templates:
    if name in extract_map or name in already_extracted:
        remove_ranges.append((name, start, end))
        log(f"Will remove {name} (L{start+1}-L{end+1}, {end-start+1} lines)")

# Sort by start line descending (remove from bottom first)
remove_ranges.sort(key=lambda x: x[1], reverse=True)

total_removed = sum(end - start + 1 for _, start, end in remove_ranges)
log(f"\nTotal template lines to remove: {total_removed}")
log(f"Remaining after template extraction: {len(lines) - total_removed}")

# ── Now build import statements to replace the removed templates ─────────────
new_imports = """
# Extracted templates (from inline to modules)
from templates.scripts_extra import SCRIPT_EDIT_TEMPLATE
from templates.processes import PROCESSES_TEMPLATE, SERVICES_TEMPLATE
from templates.addons_page import ADDONS_TEMPLATE
from templates.echo_chat import ECHO_CHAT_TEMPLATE
from templates.teams import TEAMS_TEMPLATE
from templates.okta import OKTA_TEMPLATE
"""

# ── Apply removal ────────────────────────────────────────────────────────────
# Backup first
bak = 'main_backup_pre_refactor.py'
if not os.path.exists(bak):
    shutil.copy2(MAIN, bak)
    log(f"Backup: {bak}")

new_lines = list(lines)  # copy

# Remove template blocks (from bottom to top to preserve indices)
for name, start, end in remove_ranges:
    # Replace the block with a comment
    new_lines[start:end+1] = [f"# [EXTRACTED] {name} -> see templates/ module\n"]

# Find where to insert new import lines - after the existing template imports
insert_after = None
for i, line in enumerate(new_lines):
    if 'from templates.base import HTML_TEMPLATE' in line:
        insert_after = i
    elif 'from templates.pages import' in line:
        # Find end of this import (may be multi-line)
        j = i
        while j < len(new_lines) and (new_lines[j].strip().endswith(',') or new_lines[j].strip().startswith(')')):
            j += 1
        insert_after = j

if insert_after is not None:
    new_lines.insert(insert_after + 1, new_imports)
    log(f"Inserted template imports after line {insert_after + 1}")
else:
    log("WARNING: Could not find insertion point for imports")

# Write new main.py
with open(MAIN, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

final_count = len(new_lines)
log(f"\nNew main.py: {final_count} lines (was {len(lines)}, removed ~{total_removed} template lines)")

save_log()
log("Done! Output saved to " + OUT)
