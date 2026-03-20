#!/usr/bin/env python3
"""
Module Command Center — Auto-Installer
Patches MasterChief main.py and nav template automatically.

Usage:
    python3 install.py                          # auto-detect main.py
    python3 install.py --main /path/to/main.py  # explicit path
    python3 install.py --dry-run                # preview changes, no writes
    python3 install.py --undo                   # restore from backup
"""
import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── ANSI colors ───────────────────────────────────────────────────────────────
G  = '\033[92m'   # green
Y  = '\033[93m'   # yellow
R  = '\033[91m'   # red
B  = '\033[94m'   # blue
DIM= '\033[2m'
W  = '\033[97m'   # white bold
RST= '\033[0m'

def ok(msg):   print(f"  {G}✅{RST} {msg}")
def warn(msg): print(f"  {Y}⚠{RST}  {msg}")
def err(msg):  print(f"  {R}❌{RST} {msg}")
def info(msg): print(f"  {B}→{RST}  {msg}")
def head(msg): print(f"\n{W}{msg}{RST}")

# ════════════════════════════════════════════════════════════════
#  SNIPPETS TO INJECT
# ════════════════════════════════════════════════════════════════

REGISTRY_BLOCK = '''
# ── Module Registry Integration ─────────────────────────────────────────────
# Auto-injected by Module Command Center install.py — do not remove this block
import json as _json
from pathlib import Path as _Path

_REGISTRY_PATH = _Path(__file__).parent / 'addons' / 'registry.json'
_MODULE_REGISTRY: dict = {}

def _load_module_registry():
    global _MODULE_REGISTRY
    try:
        if _REGISTRY_PATH.exists():
            _MODULE_REGISTRY = _json.loads(_REGISTRY_PATH.read_text(encoding='utf-8'))
    except Exception as _e:
        print(f"[registry] Failed to load: {_e}")

_load_module_registry()

@app.route('/api/registry')
def api_module_registry():
    _load_module_registry()
    return jsonify(_MODULE_REGISTRY)

@app.route('/api/nav-sections')
def api_nav_sections():
    _load_module_registry()
    return jsonify({
        'sections':      _MODULE_REGISTRY.get('_nav_sections', []),
        'total_modules': _MODULE_REGISTRY.get('count', 0),
    })

@app.route('/api/capabilities')
def api_capabilities():
    _load_module_registry()
    cap_map: dict = {}
    for slug, m in _MODULE_REGISTRY.get('modules', {}).items():
        for cap in m.get('capabilities', []):
            cap_map.setdefault(cap, []).append(slug)
    return jsonify(cap_map)
# ── End Module Registry Integration ─────────────────────────────────────────
'''

SIDEBAR_DIV = '<!-- MODULE-NAV-INJECT -->\n        <div id="sidebar-modules"></div>'

SIDEBAR_JS = '''
<script>
/* Module Command Center — auto nav injection */
(async function injectModuleNav() {
  try {
    const r = await fetch('/api/nav-sections');
    const d = await r.json();
    const el = document.getElementById('sidebar-modules');
    if (!el || !d.sections || !d.sections.length) return;
    el.innerHTML = d.sections.map(s => `
      <div class="nav-section" style="margin-top:12px">
        <div style="font-size:9px;letter-spacing:.25em;color:var(--dim,#4a6070);
          padding:4px 16px;font-weight:700">${s.icon || ''} ${s.label.toUpperCase()}</div>
        ${s.items.map(i => `
          <a href="${i.url}" class="nav-item addon-nav-link"
             style="border-left-color:${i.color || '#f5a623'};display:flex;
             align-items:center;gap:8px;padding:7px 16px;color:var(--text,#cdd6e0);
             text-decoration:none;font-size:12px;transition:background .15s"
             onmouseover="this.style.background='rgba(245,166,35,.06)'"
             onmouseout="this.style.background=''"
          >${i.icon || '📦'} ${i.label}</a>`).join('')}
      </div>`).join('');
  } catch(e) {
    console.warn('[module-nav] inject failed:', e.message);
  }
})();
</script>
'''

MARKER_START = '# ── Module Registry Integration'
MARKER_END   = '# ── End Module Registry Integration'
NAV_MARKER   = '<!-- MODULE-NAV-INJECT -->'
JS_MARKER    = '/* Module Command Center — auto nav injection */'


# ════════════════════════════════════════════════════════════════
#  FIND main.py
# ════════════════════════════════════════════════════════════════

def find_main_py(hint: str = None) -> Path:
    candidates = []
    if hint:
        candidates.append(Path(hint))

    # Walk up from this script's location
    here = Path(__file__).resolve().parent
    for p in [here, here.parent, here.parent.parent,
              here.parent.parent.parent, here.parent.parent.parent.parent]:
        c = p / 'main.py'
        if c.exists():
            candidates.append(c)

    # Also check cwd
    cwd_main = Path.cwd() / 'main.py'
    if cwd_main.exists():
        candidates.append(cwd_main)

    # Deduplicate while preserving order
    seen, unique = set(), []
    for c in candidates:
        k = str(c.resolve())
        if k not in seen:
            seen.add(k)
            unique.append(c.resolve())

    # Filter to files that look like Flask apps
    flask_mains = []
    for c in unique:
        if not c.exists():
            continue
        src = c.read_text(encoding='utf-8', errors='replace')
        if 'Flask' in src and 'app.route' in src:
            flask_mains.append(c)

    return flask_mains[0] if flask_mains else (unique[0] if unique else None)


# ════════════════════════════════════════════════════════════════
#  FIND nav / sidebar templates
# ════════════════════════════════════════════════════════════════

def find_nav_templates(main_py: Path) -> list:
    """
    Find HTML/Jinja templates that contain sidebar/nav markup.
    Looks for files with 'nav', 'sidebar', 'base', 'layout' in name,
    or files that contain sidebar-related HTML patterns.
    """
    root = main_py.parent
    candidates = []

    # Walk templates/ folder
    for tmpl_dir in [root / 'templates', root / 'static', root]:
        if not tmpl_dir.exists():
            continue
        for f in tmpl_dir.rglob('*.html'):
            name = f.name.lower()
            src  = ''
            try:
                src = f.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue
            # Score the file
            score = 0
            if any(k in name for k in ['nav', 'sidebar', 'base', 'layout', 'shell']): score += 10
            if 'sidebar' in src.lower(): score += 5
            if '<nav' in src.lower():    score += 3
            if 'nav-item' in src:        score += 3
            if 'Flask' not in src and 'route' not in src: score += 1
            if score > 0:
                candidates.append((score, f))

    candidates.sort(key=lambda x: -x[0])
    return [f for _, f in candidates[:5]]


# ════════════════════════════════════════════════════════════════
#  PATCH main.py
# ════════════════════════════════════════════════════════════════

def patch_main(main_py: Path, dry_run: bool) -> bool:
    src = main_py.read_text(encoding='utf-8')

    if MARKER_START in src:
        ok(f"Registry block already present in {main_py.name}")
        return True

    # Find best insertion point — after app = Flask(...)
    # Try several patterns in order of preference
    patterns = [
        r'(app\s*=\s*Flask\s*\([^)]*\)\s*\n)',
        r'(app\s*=\s*Flask\s*\(__name__\)\s*\n)',
        r'(from flask import[^\n]+\n)',
    ]
    insert_pos = None
    for pat in patterns:
        m = re.search(pat, src)
        if m:
            insert_pos = m.end()
            break

    if insert_pos is None:
        err(f"Could not find Flask app initialization in {main_py.name}")
        err("Add manually — see INTEGRATION.md")
        return False

    new_src = src[:insert_pos] + REGISTRY_BLOCK + src[insert_pos:]
    context = src[max(0,insert_pos-60):insert_pos].strip().split('\n')[-1]
    info(f"Inserting after: {DIM}{context}{RST}")

    if dry_run:
        warn(f"[DRY RUN] Would patch {main_py}")
        print(f"\n{DIM}--- SNIPPET PREVIEW (first 20 lines) ---{RST}")
        for line in REGISTRY_BLOCK.split('\n')[:20]:
            print(f"  {DIM}{line}{RST}")
        print(f"  {DIM}  ...{RST}")
    else:
        backup = main_py.with_suffix(f'.py.bak-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
        shutil.copy2(main_py, backup)
        info(f"Backup: {backup.name}")
        main_py.write_text(new_src, encoding='utf-8')
        ok(f"Patched {main_py.name} (+{len(REGISTRY_BLOCK.splitlines())} lines)")
    return True


# ════════════════════════════════════════════════════════════════
#  PATCH nav template
# ════════════════════════════════════════════════════════════════

def patch_template(tmpl: Path, dry_run: bool) -> bool:
    src = tmpl.read_text(encoding='utf-8')

    added_div = False
    added_js  = False

    # 1. Add sidebar div — only if not already present
    if NAV_MARKER not in src:
        # Find a good insertion point: closing </nav>, </aside>, or end of sidebar div
        insertion_patterns = [
            (r'(</nav>)', r'\1\n        ' + SIDEBAR_DIV),
            (r'(</aside>)', r'\1\n        ' + SIDEBAR_DIV),
            (r'(id=["\']sidebar["\'][^>]*>)', r'\1\n        ' + SIDEBAR_DIV),
            (r'(class=["\'][^"\']*sidebar[^"\']*["\'][^>]*>)', r'\1\n        ' + SIDEBAR_DIV),
        ]
        for pat, repl in insertion_patterns:
            new_src, n = re.subn(pat, repl, src, count=1, flags=re.IGNORECASE)
            if n:
                src = new_src
                added_div = True
                break
        if not added_div:
            # Fallback: append before </body>
            if '</body>' in src:
                src = src.replace('</body>', '        ' + SIDEBAR_DIV + '\n</body>', 1)
                added_div = True
    else:
        ok(f"Sidebar div already present in {tmpl.name}")

    # 2. Add JS — only if not already present
    if JS_MARKER not in src:
        if '</body>' in src:
            src = src.replace('</body>', SIDEBAR_JS + '\n</body>', 1)
            added_js = True
        elif '</html>' in src:
            src = src.replace('</html>', SIDEBAR_JS + '\n</html>', 1)
            added_js = True
    else:
        ok(f"Nav JS already present in {tmpl.name}")

    if not added_div and not added_js:
        return True  # nothing to do

    if dry_run:
        warn(f"[DRY RUN] Would patch template: {tmpl.name}")
        if added_div: info("  + sidebar div placeholder")
        if added_js:  info("  + nav injection script")
    else:
        backup = tmpl.with_suffix(f'{tmpl.suffix}.bak-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
        shutil.copy2(tmpl, backup)
        info(f"Backup: {backup.name}")
        tmpl.write_text(src, encoding='utf-8')
        if added_div: ok(f"Added sidebar placeholder to {tmpl.name}")
        if added_js:  ok(f"Added nav injection JS to {tmpl.name}")
    return True


# ════════════════════════════════════════════════════════════════
#  UNDO
# ════════════════════════════════════════════════════════════════

def undo(main_py: Path):
    head("Restoring backups…")
    parent = main_py.parent
    restored = 0
    for f in sorted(parent.rglob('*.bak-*'), reverse=True):
        original = f.with_name(re.sub(r'\.bak-\d{8}-\d{6}$', '', f.name))
        # Also handle .html.bak-...
        if '.html.bak-' in f.name:
            original = f.with_name(f.name[:f.name.index('.bak-')])
        elif '.py.bak-' in f.name:
            original = f.with_name(f.name[:f.name.index('.bak-')])

        if not original.exists():
            continue
        # Only restore the most recent backup (list is sorted reverse)
        if restored == 0 or str(original) not in [str(x) for x in [main_py]]:
            shutil.copy2(f, original)
            ok(f"Restored {original.name} from {f.name}")
            restored += 1
    if not restored:
        warn("No backups found")


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Module Command Center installer')
    parser.add_argument('--main',    help='Path to main.py (auto-detected if omitted)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--undo',    action='store_true', help='Restore from backup')
    parser.add_argument('--no-templates', action='store_true', help='Skip template patching')
    args = parser.parse_args()

    print(f"\n{W}{'─'*55}")
    print("  MODULE COMMAND CENTER — INSTALLER")
    print(f"{'─'*55}{RST}")

    # ── Find main.py ──────────────────────────────────────────
    head("Locating MasterChief main.py…")
    main_py = find_main_py(args.main)
    if not main_py:
        err("Could not find main.py — pass --main /path/to/main.py")
        sys.exit(1)
    ok(f"Found: {main_py}")

    if args.undo:
        undo(main_py)
        return

    # ── Patch main.py ─────────────────────────────────────────
    head("Patching main.py…")
    if not patch_main(main_py, args.dry_run):
        err("main.py patch failed — apply manually (see INTEGRATION.md)")

    # ── Find and patch nav templates ──────────────────────────
    if not args.no_templates:
        head("Finding nav/sidebar templates…")
        templates = find_nav_templates(main_py)
        if templates:
            for i, t in enumerate(templates):
                info(f"  [{i}] {t.relative_to(main_py.parent)}")
            print()

            # If only one candidate, patch it automatically
            if len(templates) == 1:
                patch_template(templates[0], args.dry_run)
            else:
                # Ask which one
                if sys.stdin.isatty():
                    print(f"  {Y}Multiple templates found. Which to patch?{RST}")
                    print(f"  {DIM}(Enter number, or 'all', or 'skip'){RST}")
                    choice = input("  > ").strip().lower()
                    if choice == 'all':
                        for t in templates:
                            patch_template(t, args.dry_run)
                    elif choice == 'skip':
                        warn("Skipping template patch — add sidebar div/JS manually (see INTEGRATION.md)")
                    elif choice.isdigit() and int(choice) < len(templates):
                        patch_template(templates[int(choice)], args.dry_run)
                    else:
                        warn("Invalid choice — skipping template patch")
                else:
                    # Non-interactive: patch the top candidate
                    info(f"Non-interactive mode — patching top candidate: {templates[0].name}")
                    patch_template(templates[0], args.dry_run)
        else:
            warn("No nav templates found automatically")
            info("Add manually to your sidebar template:")
            print(f"\n  {DIM}<!-- in your sidebar HTML -->{RST}")
            print(f"  {DIM}<div id=\"sidebar-modules\"></div>{RST}")
            print(f"\n  {DIM}<!-- before </body> -->{RST}")
            print(f"  {DIM}<script> ... see INTEGRATION.md ... </script>{RST}\n")

    # ── Write / refresh registry.json ─────────────────────────
    head("Writing initial registry.json…")
    addons_dir    = main_py.parent / 'addons' / 'modules'
    registry_path = main_py.parent / 'addons' / 'registry.json'
    if addons_dir.exists():
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from registry import Registry
            reg  = Registry(addons_dir, registry_path)
            data = reg.discover()
            ok(f"registry.json written — {data['count']} modules discovered")
            if data['count']:
                for slug, m in data['modules'].items():
                    info(f"  {m['icon']} {m['label']} [{m['category']}]")
        except Exception as e:
            warn(f"Could not auto-write registry.json: {e}")
            info("Run Module Command Center and click 'Re-discover All' to generate it")
    else:
        warn(f"addons/modules/ not found at {addons_dir}")
        info("Registry will be built when you first open Module Command Center")

    # ── Done ──────────────────────────────────────────────────
    print(f"\n{G}{'─'*55}")
    print("  DONE")
    print(f"{'─'*55}{RST}")

    if not args.dry_run:
        print(f"""
  Next steps:
  {G}1.{RST} Restart MasterChief (main.py)
  {G}2.{RST} Open Module Command Center in your browser
  {G}3.{RST} All modules now auto-appear in the MasterChief nav

  To undo all changes:
    {DIM}python3 install.py --undo{RST}

  Need help? See INTEGRATION.md
""")
    else:
        print(f"\n  {Y}Dry run complete — no files were modified{RST}")
        print(f"  Run without --dry-run to apply changes\n")


if __name__ == '__main__':
    main()
