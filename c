[33ma219e92[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m v2.2.6
[33m3671d09[m Merge branch 'main' of https://github.com/jbalestrine/masterchief
[33m11b9838[m[33m ([m[1;33mtag: [m[1;33mv2.2.6[m[33m)[m Bump version to 2.2.6
[33m739f093[m Delete data/echo_training directory
[33m009bb4e[m[33m ([m[1;33mtag: [m[1;33mv2.2.4[m[33m)[m v2.2.4: fix RBAC login - use current_app instead of broken 'from main import', fallback auth always available
[33m096c79d[m[33m ([m[1;33mtag: [m[1;33mv2.2.3[m[33m)[m v2.2.3: fix managers importlib loading, login fallback auth, missing data files (api_settings.json, cert_audit.json, features/templates, managers/data)
[33maa5e177[m[33m ([m[1;33mtag: [m[1;33mv2.2.2[m[33m)[m v2.2.2: include templates, static, root modules for full web GUI support
[33mfb5cf86[m[33m ([m[1;33mtag: [m[1;33mv2.2.1[m[33m)[m v2.2.1: bundle web GUI (main.py+HTML) in package, fix missing module files
[33m5502e0e[m[33m ([m[1;33mtag: [m[1;33mv2.2.0[m[33m)[m v2.2.0: add masterchief serve command for web GUI
[33med750f2[m[33m ([m[1;33mtag: [m[1;33mv2.1.1[m[33m)[m v2.1.1: move ansible to own extra, unblock cloud install
[33m4d12745[m[33m ([m[1;33mtag: [m[1;33mv2.1.0[m[33m)[m v2.1.0: full package discovery (123 packages/23 modules), cloud deps optional, updated MANIFEST.in
[33mb205f30[m[33m ([m[1;33mtag: [m[1;33mv2.0.0[m[33m)[m Release v2.0.0 — PyPI publish
[33ma8a2c90[m Fix gallery lightbox: event delegation for reliable image click-to-view
[33md6dceb5[m Art Gallery: purchase system, cart, checkout, admin login & edit panel
[33m39f8b51[m Add Art Gallery, setup_wizard, dataset_helper, platform proxy
[33ma832767[m Delete .github/workflows directory
[33m171f36b[m Milestone: MasterChief v1.1.0 - ARM Creator, TF Wizard CAF, dependency fixes
[33m93de3a7[m Dev full setup (#44)
[33mfcbb178[m Remove mkdocs-material from requirements.txt
[33m1c762c9[m Add mkdocs-material to requirements
[33m0757352[m Update repository URL to include .git extension
[33m8086e55[m Revise mkdocs.yml for project documentation setup
[33mde93c58[m Create mkdocs.yml for documentation configuration
[33m1421abc[m Add .readthedocs.yaml configuration file
[33m84a3ac0[m Rename .readthedocs.yaml to mkdocs.yaml
[33m50a44cb[m Create .readthedocs.yaml for MkDocs setup
[33m167f4a2[m Fix NameError: add missing import random
[33m37c7611[m YouTube: switch to YT.Player API for reliable autoplay; fix chat inline player; fix \s SyntaxWarnings
[33m3c449c2[m chore: untrack .claude/ from repo
[33maddc792[m fix: rsg_version=1.2 required for WebView node (was 1.1), bump build_version=4
[33m71dc138[m fix: exclude broken legacy panel XMLs from zip (caused blank screen)
[33m9f633d5[m fix: move WebView uri init() to component script (blank screen fix)
[33mebbe4fd[m fix: setFocus(true) on WebView + focusable attr (blank screen fix)
[33m893512f[m chore: rebuild roku zip with WebView loading ciacpu.myddns.me:8080
[33mab1a424[m fix: use RSG WebView node to load ciacpu.myddns.me:8080 persistently (type=webapp exits on nav)
[33me3d31ab[m fix: switch to type=webapp + webapp_url=http://ciacpu.myddns.me:8080/ (roHtmlWidget removed in Roku OS 9+)
[33mc7f7ac3[m fix: load http://ciacpu.myddns.me:8080/
[33m73cfb7a[m fix: roHtmlWidget load http://127.0.0.1:8080
[33mda0b405[m feat: replace IPTV loader with roHtmlWidget -> ciacpi.myddns.me:8080
[33m44481cb[m fix: AsyncGetToFile for 7MB playlist + alpha groups when no group-title
[33ma5d505f[m fix: M3UTask compile - no goto, stri() for int, forward comma scan
[33m3fd9480[m feat: M3U browser - fetch get.php m3u, parse groups+channels, browse and play
[33m75fae78[m refactor: strip to IPTV-only - remove all DevOps tabs, MainScene is now a pure Live TV channel browser
[33mc538f07[m fix: re-assert scene focus every timer tick - prevents API callbacks from stealing focus
[33mfd3f07e[m feat: IPTV uses Xtream Codes API (categories+streams JSON, no M3U download); fix ApiTask array wrapping
[33m197759f[m fix: tab switching (re-focus scene after showPanel) + M3U reload no-op + CR strip + 5K channel cap
[33m3d85c24[m fix: PipelinesPanel crash - statusLbl used m.rowGroup before it was created (null-ref on init)
[33m6822e49[m fix: replace exit while with return in findLastComma - exit while unsupported in BrightScript
[33md87dcc6[m fix: replace goto/label with if-else in parseM3U - goto unsupported in RSG BrightScript
[33m549aee2[m fix: remove all top-level CONST from XML script blocks - invalid in BrightScript (same rule as .brs files). Convert to m.* instance vars in init()
[33m91f425e[m fix: replace all iif() with if/then/else - iif() is not a BrightScript built-in
[33ma6e4349[m fix: remove duplicate statusColor/safeStr/rp from all panels - RSG auto-includes source/*.brs causing dup function compile error
[33m33c4cd1[m fix: remove _ line continuation from formatTs() in panelUtils.brs (BrightScript compile error line 39)
[33m1ffce31[m fix: remove top-level CONST from panelUtils.brs - BrightScript only allows CONST inside XML script blocks, not standalone .brs files
[33m26dad6d[m fix: rebuild zip - manifest must be FIRST entry and STORED (not deflated) for Roku installer
[33m17991c2[m fix: ASCII-sanitize ALL roku files - BrightScript parser is ASCII-only (em-dash, arrows, box-drawing chars caused silent crash)
[33m08b4050[m fix: strip ALL 4-byte emoji from roku components (EchoPanel robot, NotifsPanel bell, PipelinesPanel refresh)
[33mc0018b8[m fix: remove 4-byte emoji (U+1FXXX) from BrightScript - crashes Roku parser
[33mb9977f9[m fix: update BASE_URL 127.0.0.1 -> 10.0.0.159 in all Roku panels (Roku can't reach localhost)
[33m68fdf09[m feat: IPTV Live TV tab - M3U playlist browser + full-screen video player
[33ma27616e[m fix: roku - add type=appl/rsg_version to manifest, fix row children targeting rowGroup not m.top
[33m16b4d0f[m chore: add pre-built roku channel zip for direct sideload
[33m313aaec[m feat: Roku SceneGraph channel - MasterChief DevOps dashboard for TV
[33mb14732e[m fix: strip UTF-8 BOM + fix backslash-in-f-string (Python <3.12 compat)
[33mffd79d2[m fix: add IMAGE_CACHE/IMAGE_RATE/IMAGE_JOBS globals + update requirements.txt (Flask-SocketIO, bcrypt, python-jose, PyGithub, Pillow)
[33m8f49c8e[m chore: clean up requirements.txt — core deps only, move heavy optional deps
[33m1a4d973[m chore: untrack large model files (*.gguf, Files_and_folders.csv) — add to .gitignore
[33m5b40730[m testjbx
[33m3d37634[m test
[33mfda3b63[m test
[33m149696b[m feat: source control manager (/sys/scm) + export active files as ZIP (/sys/api/export-active)
[33m2e7b3d8[m[33m ([m[1;33mtag: [m[1;33mv02-25-1980[m[33m)[m fix: reduce scanner noise — skip data/backups/platform.bak/webapp dirs from orphan scan
[33m1a193ff[m fix: remove duplicate const dryRun declaration in sweep modal (SyntaxError line 1421)
[33mbbb0332[m fix: paginate diagnostics tables (200/page) — was freezing browser with 7000+ DOM nodes
[33mdd883e4[m fix: make diagnostics applyData() fault-tolerant — isolate buildGraph D3 crash
[33m38cb8c1[m[33m ([m[1;33mtag: [m[1;33mv1.4.0[m[33m)[m fix: restore swept files + protect package dirs from orphan scan
[33m526f90a[m feat: orphan sweep — incremental file cleanup with health-check gates
[33mdda9b34[m feat: inject MC_BASE_URL and MC_PORT into addon subprocess envs
[33md47f5aa[m feat: /sys/diagnostics - full-repo AST scanner, Visio-style D3 graph, inspector panel, issues feed, services panel
[33md099422[m chore: ignore nul file artifact
[33m0117295[m MILESTONE: modules loader working - Open App links fixed, port conflict auto-resolve, pin to nav, blank module creation, JS syntax fixes
[33md0bcbe6[m[33m ([m[1;33mtag: [m[1;33mgot-modules-loader-working-for-python-in-UI[m[33m)[m got modules loader working for python in UI
[33m33216a4[m perf: pre-warm conversation storage at startup to eliminate cold-start latency
[33m2e5206a[m revert: restore echo_chat to original versions (pre-fix)
[33mbeb97a1[m fix: echo_chat page - fix JS syntax error in fetchModels, fix m.get() Python syntax in loadSession, add fetchSessions init call, add missing CSS btn classes; update /echo-chat route to serve standalone page; fix same m.get() in embedded template
[33m40b9f00[m Restore missing standalone HTML files (secrets_vault, pipelines, notifications, rbac)
[33m7879796[m Restore web_ide.html (was accidentally untracked)
[33m056ac57[m Restore accidentally deleted package source files (utils, templates, renderers, blueprints)
[33mca3fef9[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/main[m[33m)[m Teams: auto-switch to chat tab on login, fix PS graph poll success path
[33mc9c3294[m checkpoint: App Gateway cert tab, Sprint DV wizard, demo mode, backend routes
[33mcd40dd7[m Fix modules page JS wiring: regex escaping, API field names, prefs shape
[33m2b370c7[m Addon module system: per-module port isolation, Flask run() monkeypatch, delete route, fuzzy entry-point detection, install.php support
[33mbd86e03[m Remove unused manager classes: Script, Vault, Memory
[33me90cfca[m[33m ([m[1;33mtag: [m[1;33mcheckpoint-login-system-v1.0[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/fixClaude[m[33m)[m feat: Implement RBAC-based login system with public and admin access
[33m6ac105a[m Add GitHub Integration: Remote repo browsing, file type filtering, and dashboard button
[33m1ee951a[m GITHUB remote load. it works.
[33m9ac1824[m added Create Blank Module feature to ADDONS page - wizard interface for creating empty modules with proper directory structure and file templates
[33m590128c[m fixed AI code analyzer pattern matching to prevent false greeting detection when code contains words like 'hello'
[33m31510fe[m added AI code analyzer, fixed main echo-chat to load models and training with temp and weights.
[33m1c8553c[m Checkpoint: updated main IDE and CAF files
[33m4575c14[m updated main ide and caf, fixed bug with literals causing null callsfor onclick
[33meb32112[m fixClaude: restore missing manager classes, API routes, fix JS/CSS in web_ide
[33m03eef27[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/feature-tf-wizard-caf-lite[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/claude-frosty-rubin[m[33m)[m Remove shoutcast and jamroom functionality, add enterprise authentication system
[33m2aa56ad[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/feature-tf-wizard-caf[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/claude-wonderful-cannon[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/claude-cool-elbakyan[m[33m)[m Add /web_tf_wizard route to serve web_tf_wizard.html; remove accidental inline Python in template
[33m658cef3[m Remove large files from commit and add .gitignore
[33mc133c4d[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/restore-1.2.1[m[33m)[m working version. patched for image creation.
[33m324ddc1[m added updates to web ide logic and chat
[33m5e5b30c[m logic for chat upgraded, webide upgraded
[33m169d5c7[m 2/7
[33m25bd559[m fix: move ECHO_TRAINING_TEMPLATE out of JS and fix indentation; add scripts/post_chat.py for smoke tests
[33m95bd772[m fixed errors with sleep.
[33mf25c6b1[m[33m ([m[1;33mtag: [m[1;33mv1.2.1[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/chat_bot_featuresv0.02[m[33m)[m chore(release): v1.2.1 — training UI, dataset helpers, upload validation
[33m9fe94c7[m ui: show persona badges, add session selector, enable persona action, persona status API, and log persona enable
[33m880c895[m personality: add persona upload flag, session toggle, editor UI, include persona in chat
[33m94b34d8[m resources: add training-example on upload; enqueue test script
[33m5b9be48[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/restore-gguf[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-revert-[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-restore-20260117-2[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-chat_bot_featuresv0.02[m[33m)[m new changes for training module test.
[33md61ef06[m Add npm install and Chocolatey deployment support for masterchief (#41)
[33mdd07ad9[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-revert-20260117-003514[m[33m, [m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-gguf-revert-2ee5ae9[m[33m)[m Add Echo Starlite chat interface to web GUI with training capabilities (#40)
[33mb2e8c7b[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/backup-before-reset-[m[33m)[m Add MasterChief Complete Package README for 2026-01-13 release
[33m9f515f7[m Add interactive scenario-based script generation to Echo (#37)
[33mdd1f74d[m Add visual image display for Echo Starlite identity (#36)
[33mfb21b0f[m Add AI-powered code generation CLI with interactive prompts (#35)
[33m8e29703[m Add persistent conversation storage for Echo Starlite bot (#34)
[33m0a99ff7[m Add live chat bot with training capabilities for Echo (#32)
[33mf448aeb[m Add single-file Flask web app with embedded HTML for MasterChief platform (#31)
[33m07cd850[m Add fully integrated web GUI for uploadable bot training data with one-command startup (#33)
[33m1c1830d[m Fix mypy type errors and add PyYAML type stubs (#30)
[33mbd0b665[m Implement Echo DevOps Master Suite: Natural language DevOps automation across 10 lifecycle phases (#28)
[33m078899e[m Add Echo Personality Mod System with weather-driven AI presence and character voices (#27)
[33m44f66f9[m Add Echo script and architecture generation engine (#26)
[33m6ae922a[m Add Echo Starlite visual identity system with angel ASCII art representation (#25)
[33md88dfcd[m Add voice automation system with wake word detection and natural language control (#24)
[33m8a82410[m Add comprehensive script automation suite with AI generation, templates, validation, and scheduling (#23)
[33m7e41b41[m Add voice cloning capability to IRC Bot (#22)
[33m32d9019[m Add local voice/audio system for IRC bot with TTS, STT, recording, and announcements (#21)
[33m5d7579a[m Add comprehensive data ingestion system for IRC bot (#20)
[33me6fd9c1[m Fix flake8 CI failure caused by platform module shadowing (#18)
[33ma2cb689[m [WIP] Fix flake8 errors in CI workflow for Python 3.12 (#15) (#16)
[33mb3eed0d[m Implement DevOps script library, script generation wizard, and enhanced CLI (#12)
[33m1edbf94[m Implement Phase 1 & 2: Event-driven infrastructure with real-time WebSocket communication (#9)
[33mf4ee781[m Remove invalid Python package name `module-loader` (#13)
[33mbb573bf[m Add Echo voice system for task execution feedback (#29)
[33mc551e18[m Remove invalid Python package name core/module-loader (#19)
[33m92920b3[m [WIP] Fix flake8 command in GitHub Actions workflow (#17)
[33m551d14b[m [WIP] Rename module-loader directory to module_loader (#14)
[33m4963bdb[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/develop[m[33m)[m [WIP] Build complete production-ready DevOps platform (#11)
[33mdadac7c[m [WIP] Implement DevOps Web GUI architecture without Docker (#10)
[33mf7619d0[m Implement Phase 1: Event Bus and State Store infrastructure
[33m779d938[m Initial plan
[33m9aac742[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/dash-to-underscore-fix[m[33m)[m [WIP] Merge existing modular codebase into main branch (#6)
[33mc4ca9dd[m Initial plan
[33m2e922af[m [WIP] Fix type-check workflow file permissions and documentation (#5)
[33m3bfca01[m Initial plan
[33m2b2f6aa[m Implement modular DevOps automation platform with multi-IaC support (#1)copilot/create-devops-automation-foundation
[33m8c9d8b8[m Merge pull request #2 from jbalestrine/Test
[33m951d432[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/Test[m[33m)[m Merge branch 'main' into Test
[33m4e5d76c[m Merge pull request #3 from jbalestrine/copilot/add-bootable-os-distribution
[33m481fb86[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/copilot-add-bootable-os-distribution[m[33m)[m Implement MasterChief Enterprise DevOps Platform with bootable OS and system management
[33me70b5e7[m[33m ([m[1;33mtag: [m[1;33marchive/2026-02-25/copilot-complete-implementation-devops-platform[m[33m)[m Add implementation completion summary document
[33ma5c0674[m Fix GitHub Actions security: Add explicit GITHUB_TOKEN permissions
[33m6e7fd71[m Add validation script to verify platform structure
[33m07b8a1c[m Add implementation summary, demo script, and Python package structure
[33m23ea371[m Fix code review issues: JSON comments, error handling, async lock usage, import duplication
[33m49586bb[m Implement MasterChief Enterprise DevOps Platform with bootable OS and system management
[33m7b8e981[m Add examples, observability configs, Helm charts, and documentation
[33mb8ff4ba[m Implement core platform foundation with modules and documentation
[33m92ffdf4[m Initial plan
[33mb1766bd[m Initial plan
[33mc194a43[m Add files via upload
[33me012246[m Add files via upload
[33mda4c595[m Initial commit
