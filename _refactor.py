"""
Automated refactoring script for main.py.

Phase 1: Extract inline HTML templates to templates/ modules.
Phase 2: Create route blueprints in routes/.
Phase 3: Rewrite main.py to import from new modules.
"""
import re
import os

MAIN = 'main.py'
MAIN_BAK = 'main_backup_pre_refactor.py'

# ── Phase 1: Extract inline templates ───────────────────────────────────────

def extract_templates():
    """Find all TEMPLATE = triple-quote blocks in main.py, write them to files."""
    with open(MAIN, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    templates = []  # (varname, start_line_idx, end_line_idx)
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match: VARNAME="""  or  VARNAME = """
        m = re.match(r'^([A-Z][A-Z_0-9]*)\s*=\s*("{3})', line)
        if m:
            varname = m.group(1)
            delim = m.group(2)
            # Count delimiters on this line
            count = line.count(delim)
            if count == 1:
                # Multi-line string - find closing
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

    print(f"Found {len(templates)} inline templates:")
    for name, start, end in templates:
        size = end - start + 1
        print(f"  {name:30s}  L{start+1:5d}-L{end+1:5d}  ({size:5d} lines)")

    return templates, lines


def write_template_files(templates, lines):
    """Write extracted templates to templates/ module files."""
    # Group templates by target file
    file_map = {
        'templates/echo_chat.py': ['ECHO_CHAT_TEMPLATE'],
        'templates/teams.py': ['TEAMS_TEMPLATE'],
        'templates/okta.py': ['OKTA_TEMPLATE'],
        'templates/addons_page.py': ['ADDONS_TEMPLATE'],
        'templates/processes.py': ['PROCESSES_TEMPLATE', 'SERVICES_TEMPLATE'],
        'templates/scripts_extra.py': ['SCRIPT_EDIT_TEMPLATE'],
    }

    # Templates that already exist in templates/base.py or templates/pages.py
    already_extracted = {
        'HTML_TEMPLATE',  # in templates/base.py
        'SCRIPTS_TEMPLATE',  # in templates/pages.py
        'SCRIPT_VIEW_TEMPLATE',  # in templates/pages.py (but may be shadowed)
        'SCRIPT_EXECUTE_TEMPLATE',  # in templates/pages.py
    }

    # Only extract templates that aren't already in the map and aren't already extracted
    unmapped = set()
    for name, start, end in templates:
        found_in_map = any(name in names for names in file_map.values())
        if not found_in_map and name not in already_extracted:
            unmapped.add(name)

    if unmapped:
        print(f"\n⚠️  Unmapped templates (will stay inline): {unmapped}")

    # Create template files
    os.makedirs('templates', exist_ok=True)

    # Build lookup: varname -> (start, end)
    tpl_lookup = {name: (start, end) for name, start, end in templates}

    for filepath, varnames in file_map.items():
        content_parts = []
        content_parts.append(f'"""\nMasterChief Template Module: {os.path.basename(filepath)}\nExtracted from main.py during refactoring.\n"""\n\n')

        for varname in varnames:
            if varname in tpl_lookup:
                start, end = tpl_lookup[varname]
                # Get the raw lines including the assignment
                tpl_lines = lines[start:end+1]
                content_parts.append(''.join(tpl_lines))
                content_parts.append('\n\n')
            else:
                print(f"  ⚠️  {varname} not found in main.py")

        full_content = ''.join(content_parts)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"  ✅ Created {filepath}")

    return file_map, tpl_lookup


# ── Phase 2: Identify route groups for blueprints ──────────────────────────

def identify_route_groups(lines):
    """Group routes by URL prefix for blueprint extraction."""
    route_funcs = []
    for i, line in enumerate(lines):
        if line.startswith('def '):
            fname = line.strip().split('(')[0].replace('def ', '')
            # Look back for route decorators
            routes = []
            j = i - 1
            while j >= 0 and (lines[j].strip().startswith('@') or lines[j].strip() == ''):
                m2 = re.search(r"@app\.route\(['\"]([^'\"]+)", lines[j])
                if m2:
                    routes.append(m2.group(1))
                j -= 1
            if routes:
                # Find function end
                end = i + 1
                while end < len(lines):
                    next_line = lines[end]
                    if next_line.strip() == '' or next_line[0] not in ' \t':
                        # Check if next non-empty line is at indentation 0
                        k = end
                        while k < len(lines) and lines[k].strip() == '':
                            k += 1
                        if k < len(lines) and lines[k][0] not in ' \t':
                            break
                        end = k
                    else:
                        end += 1
                route_funcs.append({
                    'name': fname,
                    'routes': routes,
                    'start': i,
                    'decorator_start': j + 1,
                    'end': end - 1,
                    'prefix': '/' + routes[0].strip('/').split('/')[0] if routes[0] != '/' else '/'
                })

    # Group by prefix
    from collections import defaultdict
    groups = defaultdict(list)
    for rf in route_funcs:
        groups[rf['prefix']].append(rf)

    print(f"\nRoute groups for blueprint extraction:")
    for prefix, funcs in sorted(groups.items(), key=lambda x: -len(x[1])):
        total_lines = sum(f['end'] - f['decorator_start'] + 1 for f in funcs)
        print(f"  {prefix:25s}  {len(funcs):3d} routes  ({total_lines:5d} lines)")

    return groups


# ── Phase 3: Create route blueprint files ──────────────────────────────────

def create_blueprint_files(groups, lines, tpl_lookup):
    """Create blueprint .py files for major route groups."""
    os.makedirs('routes', exist_ok=True)

    # Ensure routes/__init__.py exists
    init_path = 'routes/__init__.py'
    if not os.path.exists(init_path) or os.path.getsize(init_path) == 0:
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('"""MasterChief route blueprints."""\n')

    # Blueprint mapping: prefix -> (filename, blueprint_name)
    bp_map = {
        '/api': None,  # Too broad - will be split by sub-prefix
        '/addons': ('routes/addons.py', 'addons_bp'),
        '/sys': ('routes/system.py', 'system_bp'),
        '/gallery': ('routes/gallery.py', 'gallery_bp'),
        '/scripts': ('routes/scripts.py', 'scripts_bp'),
        '/processes': ('routes/services.py', 'services_bp'),
        '/services': ('routes/services.py', 'services_bp'),
        '/okta': ('routes/okta.py', 'okta_bp'),
        '/teams': ('routes/teams.py', 'teams_bp'),
        '/manager': ('routes/manager.py', 'manager_bp'),
        '/features': ('routes/features.py', 'features_bp'),
        '/tf_wizard': ('routes/tf_wizard.py', 'tf_wizard_bp'),
        '/echo-chat': ('routes/echo_chat.py', 'echo_chat_bp'),
    }

    # For /api routes, further split by second segment
    api_sub_map = {}
    if '/api' in groups:
        for rf in groups['/api']:
            path = rf['routes'][0]
            parts = path.strip('/').split('/')
            if len(parts) >= 2:
                sub = parts[1]
            else:
                sub = '_root'
            api_sub_map.setdefault(sub, []).append(rf)

        print(f"\n  /api sub-groups:")
        for sub, funcs in sorted(api_sub_map.items(), key=lambda x: -len(x[1])):
            total = sum(f['end'] - f['decorator_start'] + 1 for f in funcs)
            print(f"    /api/{sub:20s}  {len(funcs):3d} routes  ({total:5d} lines)")

    return bp_map, api_sub_map


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import shutil

    print("=" * 70)
    print("MasterChief main.py Refactoring Analysis")
    print("=" * 70)

    # Backup
    if not os.path.exists(MAIN_BAK):
        shutil.copy2(MAIN, MAIN_BAK)
        print(f"\n✅ Backup created: {MAIN_BAK}")
    else:
        print(f"\n⚠️  Backup already exists: {MAIN_BAK}")

    templates, lines = extract_templates()
    file_map, tpl_lookup = write_template_files(templates, lines)
    groups = identify_route_groups(lines)
    bp_map, api_sub_map = create_blueprint_files(groups, lines, tpl_lookup)

    # Summary
    print("\n" + "=" * 70)
    print("REFACTORING PLAN SUMMARY")
    print("=" * 70)

    # Count lines that will be extracted
    template_lines = sum(end - start + 1 for _, start, end in templates
                        if _ not in {'HTML_TEMPLATE', 'SCRIPTS_TEMPLATE',
                                    'SCRIPT_VIEW_TEMPLATE', 'SCRIPT_EXECUTE_TEMPLATE',
                                    'MODULES_TEMPLATE'})
    print(f"\nTemplate lines to extract: {template_lines}")

    route_lines = 0
    for prefix, funcs in groups.items():
        if prefix in {'/api', '/addons', '/sys', '/gallery', '/scripts',
                      '/processes', '/services', '/okta', '/teams',
                      '/manager', '/features', '/tf_wizard', '/echo-chat'}:
            route_lines += sum(f['end'] - f['decorator_start'] + 1 for f in funcs)
    print(f"Route lines to extract:    {route_lines}")
    print(f"Total extractable:         {template_lines + route_lines}")
    print(f"Current main.py:           {len(lines)} lines")
    print(f"Estimated after refactor:  {len(lines) - template_lines - route_lines} lines")
    print(f"\n✅ Template files created. Blueprint analysis complete.")
    print("Next step: Run the actual extraction by modifying main.py.")
