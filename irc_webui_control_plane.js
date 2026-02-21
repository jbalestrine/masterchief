(function () {
  if (window.IRCCP) return;

  /* ==========================
     CONFIG (SAFE TO EDIT)
     ========================== */
  const CONFIG = {
    apiBase: "http://127.0.0.1:8080",
    token: localStorage.getItem("irc_bridge_token") || "YOUR_TOKEN",
    channel: "#masterchief"
  };

  /* ==========================
     UI CREATION
     ========================== */
  const root = document.createElement("div");
  root.id = "irc-cp";
  root.style = `
    position: fixed;
    bottom: 0;
    right: 0;
    width: 520px;
    height: 360px;
    background: #0c0c0c;
    color: #ddd;
    font-family: monospace;
    border: 1px solid #333;
    z-index: 999999;
    display: flex;
    flex-direction: column;
  `;

  root.innerHTML = `
    <div id="irc-cp-header" style="background:#111;padding:6px;font-weight:bold;">
      IRC Control Plane
    </div>
    <div id="irc-cp-tabs" style="display:flex;border-bottom:1px solid #333;">
      <div class="tab active" data-tab="console">Console</div>
      <div class="tab" data-tab="modules">Modules</div>
      <div class="tab" data-tab="server">Server</div>
      <div class="tab" data-tab="ai">AI</div>
    </div>
    <div id="irc-cp-body" style="flex:1;overflow:auto;padding:6px;"></div>
    <input id="irc-cp-input" placeholder="/conf enable m_sasl.so"
      style="border:0;border-top:1px solid #333;
             padding:6px;background:#000;color:#0f0;">
  `;

  document.body.appendChild(root);

  /* ==========================
     STYLES
     ========================== */
  const style = document.createElement("style");
  style.textContent = `
    #irc-cp .tab {
      padding:6px 10px;
      cursor:pointer;
      border-right:1px solid #333;
    }
    #irc-cp .tab.active {
      background:#222;
      color:#0f0;
    }
  `;
  document.head.appendChild(style);

  const body = root.querySelector("#irc-cp-body");
  const input = root.querySelector("#irc-cp-input");

  function log(msg) {
    const d = document.createElement("div");
    d.textContent = msg;
    body.appendChild(d);
    body.scrollTop = body.scrollHeight;
  }

  /* ==========================
     API HELPER
     ========================== */
  async function api(path, body) {
    const res = await fetch(CONFIG.apiBase + path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-BRIDGE-TOKEN": CONFIG.token
      },
      body: body ? JSON.stringify(body) : null
    });
    return res.json();
  }

  /* ==========================
     COMMAND ENGINE (mIRC-like)
     ========================== */
  async function handle(cmd) {
    log("> " + cmd);
    const p = cmd.trim().split(/\s+/);

    switch (p[0]) {
      case "/conf":
        if (p[1] === "enable")
          await api("/features/inspircd/module/enable", { module: p[2] }),
          log("Module enabled (pending apply)");
        if (p[1] === "disable")
          await api("/features/inspircd/module/disable", { module: p[2] }),
          log("Module disabled (pending apply)");
        if (p[1] === "apply")
          await api("/features/inspircd/apply"),
          log("Config applied & rehashed");
        break;

      case "/module":
        log("Module UI coming from server config");
        break;

      case "/ai":
        const r = await api("/irc/module/stream", {
          session: "web-ui",
          module: "qwen_inspircd",
          args: ["--channel", CONFIG.channel, "--prompt", p.slice(1).join(" ")]
        });
        log("[AI] " + (r.output || "ok"));
        break;

      case "/server":
        log("Server command sent");
        break;

      default:
        log("Unknown command");
    }
  }

  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      handle(input.value);
      input.value = "";
    }
  });

  /* ==========================
     TAB HANDLING
     ========================== */
  root.querySelectorAll(".tab").forEach(tab => {
    tab.onclick = () => {
      root.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      body.innerHTML = "";
      log(`Switched to ${tab.dataset.tab}`);
    };
  });

  log("IRC Control Plane loaded.");
  log("Try: /conf enable m_sasl.so");

  window.IRCCP = { root, log };
})();
