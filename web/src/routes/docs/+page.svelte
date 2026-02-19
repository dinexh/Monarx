<script lang="ts">
  import { onMount } from 'svelte';

  const sections = [
    { id: 'overview', label: 'Overview' },
    { id: 'capabilities', label: 'Capabilities' },
    { id: 'installation', label: 'Installation' },
    { id: 'usage', label: 'Usage' },
    { id: 'configuration', label: 'Configuration' },
    { id: 'auto-start', label: 'Auto-Start' },
  ];

  let activeSection = 'overview';

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) activeSection = entry.target.id;
        });
      },
      { rootMargin: '-30% 0px -60% 0px' }
    );

    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  });
</script>

<svelte:head>
  <title>Docs — MacMonitor</title>
  <meta name="description" content="MacMonitor documentation — installation, configuration, and usage guide." />
</svelte:head>

<div class="docs-root">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-inner">
      <p class="sidebar-label">Documentation</p>
      <nav>
        {#each sections as { id, label }}
          <a
            href="#{id}"
            class="sidebar-link"
            class:active={activeSection === id}
          >{label}</a>
        {/each}
      </nav>
      <div class="sidebar-divider"></div>
      <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener" class="sidebar-github">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
        </svg>
        View on GitHub
      </a>
    </div>
  </aside>

  <!-- Main content -->
  <main class="content">

    <section id="overview" class="doc-section">
      <h1 class="doc-h1">MacMonitor</h1>
      <p class="doc-lead">A lightweight macOS menu bar application for real-time system monitoring.</p>
      <p class="doc-p">
        MacMonitor lives in your macOS menu bar and shows live CPU and memory usage at a glance.
        It uses native macOS APIs — <code>vm_stat</code>, <code>sysctl</code>, and the
        UserNotifications framework — to give you accurate, low-overhead system telemetry without
        running a heavy background service.
      </p>
      <div class="badge-row">
        <span class="badge">Python 3.9+</span>
        <span class="badge">macOS 12+</span>
        <span class="badge">MIT License</span>
        <span class="badge green">v1.0.0</span>
      </div>
    </section>

    <section id="capabilities" class="doc-section">
      <h2 class="doc-h2">Capabilities</h2>

      <div class="cap-grid">
        <div class="cap-card">
          <div class="cap-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
          </div>
          <div>
            <h3>Native Menu Bar UI</h3>
            <p>The menu bar title updates every 5 seconds: <code>C:XX% M:XX%</code>. When memory pressure or resource usage is elevated, it switches to <code>WARN</code>, <code>HIGH</code>, or <code>STRESS</code> mode automatically.</p>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/></svg>
          </div>
          <div>
            <h3>Memory Breakdown</h3>
            <p>MacMonitor reads <code>vm_stat</code> and <code>memory_pressure</code> to split RAM into four categories: <strong>Wired</strong>, <strong>Active</strong>, <strong>Compressed</strong>, and <strong>Cached</strong>. It also tracks lag risk when Compressed exceeds Active memory.</p>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"/><path d="M3 12h3m12 0h3M12 3v3m0 12v3"/></svg>
          </div>
          <div>
            <h3>Process Intelligence</h3>
            <p>The top 5 CPU and memory consumers are listed in the dropdown in real time. You can kill any process directly from the menu without opening Activity Monitor. Chrome, Electron, and Slack are automatically tagged as GPU-heavy.</p>
          </div>
        </div>

        <div class="cap-card">
          <div class="cap-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          </div>
          <div>
            <h3>Native Alerts</h3>
            <p>Threshold breaches trigger macOS UserNotifications — the same alert system used by Calendar and Mail. Alerts respect a 120-second cooldown per metric to prevent notification fatigue. Falls back to <code>osascript</code> if the framework is unavailable.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="installation" class="doc-section">
      <h2 class="doc-h2">Installation</h2>
      <p class="doc-p">MacMonitor requires Python 3.9 or later and runs on macOS 12 Monterey and above.</p>

      <h3 class="doc-h3">1. Clone the repository</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> git clone https://github.com/dinexh/Monarx.git MacMonitor</div>
        <div class="code-line"><span class="prompt">$</span> cd MacMonitor</div>
      </div>

      <h3 class="doc-h3">2. Create a virtual environment</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> python3 -m venv .venv</div>
        <div class="code-line"><span class="prompt">$</span> source .venv/bin/activate</div>
      </div>

      <h3 class="doc-h3">3. Install dependencies</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> pip install -r requirements.txt</div>
      </div>
      <p class="doc-note">Dependencies: <code>psutil</code>, <code>rumps</code>, <code>pyobjc-framework-Cocoa</code>, <code>pyobjc-framework-UserNotifications</code></p>
    </section>

    <section id="usage" class="doc-section">
      <h2 class="doc-h2">Usage</h2>
      <p class="doc-p">Run the app with Python from the project root:</p>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> python main.py</div>
      </div>
      <p class="doc-p">
        MacMonitor will appear in your menu bar as <code>C:XX% M:XX%</code> immediately.
        Click it to open the dropdown showing the full system snapshot.
      </p>

      <h3 class="doc-h3">Menu bar states</h3>
      <div class="state-table">
        <div class="state-row">
          <span class="state-code normal">C:43% M:71%</span>
          <span class="state-label">Normal — all metrics within thresholds</span>
        </div>
        <div class="state-row">
          <span class="state-code warn">WARN C:58% M:74%</span>
          <span class="state-label">Memory pressure detected at WARN level</span>
        </div>
        <div class="state-row">
          <span class="state-code high">HIGH C:91% M:83%</span>
          <span class="state-label">Memory pressure is HIGH</span>
        </div>
        <div class="state-row">
          <span class="state-code stress">STRESS C:35% M:76%</span>
          <span class="state-label">Compressed memory exceeds Active memory (lag risk)</span>
        </div>
      </div>
    </section>

    <section id="configuration" class="doc-section">
      <h2 class="doc-h2">Configuration</h2>
      <p class="doc-p">
        Thresholds can be changed at runtime via the <strong>Settings → Change Thresholds</strong> menu item,
        or by editing <code>core/config.py</code>. Saved values persist in
        <code>~/Library/Application Support/MacMonitor/config.json</code>.
      </p>

      <div class="config-table">
        <div class="config-row header">
          <span>Variable</span><span>Default</span><span>Description</span>
        </div>
        <div class="config-row">
          <code>CPU_LIMIT</code><code>85</code><span>Alert when CPU % ≥ this value</span>
        </div>
        <div class="config-row">
          <code>MEM_LIMIT</code><code>80</code><span>Alert when RAM % ≥ this value</span>
        </div>
        <div class="config-row">
          <code>SWAP_LIMIT</code><code>20</code><span>Alert when Swap % ≥ this value</span>
        </div>
        <div class="config-row">
          <code>CHECK_EVERY</code><code>5</code><span>Sampling interval in seconds</span>
        </div>
        <div class="config-row">
          <code>COOLDOWN</code><code>120</code><span>Minimum seconds between repeated alerts</span>
        </div>
      </div>

      <p class="doc-note">
        Lowering <code>CHECK_EVERY</code> increases responsiveness but also CPU usage.
        For battery-sensitive use, consider 10–30 seconds.
      </p>
    </section>

    <section id="auto-start" class="doc-section">
      <h2 class="doc-h2">Auto-Start on Login</h2>
      <p class="doc-p">
        Create a LaunchAgent plist so MacMonitor starts automatically when you log in.
        Replace <code>/path/to/MacMonitor</code> with the absolute path to your clone.
      </p>

      <h3 class="doc-h3">1. Create the plist file</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> nano ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <div class="code-block xml">
        <pre>{`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.macmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/MacMonitor/.venv/bin/python</string>
        <string>/path/to/MacMonitor/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/MacMonitor</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>`}</pre>
      </div>

      <h3 class="doc-h3">2. Load the agent</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> launchctl load ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <h3 class="doc-h3">Unload / stop</h3>
      <div class="code-block">
        <div class="code-line"><span class="prompt">$</span> launchctl unload ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <h3 class="doc-h3">Log files</h3>
      <p class="doc-p">
        MacMonitor writes logs to <code>~/Library/Logs/MacMonitor/macmonitor.log</code>.
        You can open them directly from the menu via <strong>View Logs</strong>.
      </p>
    </section>

    <div class="doc-footer">
      <p>© 2026 MacMonitor · <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">GitHub</a> · MIT License</p>
    </div>
  </main>

  <!-- Right TOC -->
  <div class="toc">
    <p class="toc-label">On this page</p>
    {#each sections as { id, label }}
      <a href="#{id}" class="toc-link" class:active={activeSection === id}>{label}</a>
    {/each}
  </div>
</div>

<style>
  .docs-root {
    display: grid;
    grid-template-columns: 220px 1fr 180px;
    min-height: 100vh;
    padding-top: 60px;
    max-width: 1280px;
    margin: 0 auto;
  }

  /* Sidebar */
  .sidebar {
    position: sticky;
    top: 60px;
    height: calc(100vh - 60px);
    overflow-y: auto;
    border-right: 1px solid var(--border);
    padding: 32px 0;
  }

  .sidebar-inner {
    padding: 0 24px;
  }

  .sidebar-label {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 12px;
  }

  .sidebar-link {
    display: block;
    padding: 7px 12px;
    font-size: 13.5px;
    color: var(--text-muted);
    border-radius: 6px;
    transition: color 0.15s, background 0.15s;
    margin-bottom: 2px;
    border-left: 2px solid transparent;
  }

  .sidebar-link:hover {
    color: #fff;
    background: var(--white-glow);
  }

  .sidebar-link.active {
    color: #fff;
    border-left-color: #3b82f6;
    background: rgba(59,130,246,0.06);
  }

  .sidebar-divider {
    height: 1px;
    background: var(--border);
    margin: 20px 0;
  }

  .sidebar-github {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: var(--text-dim);
    padding: 6px 12px;
    border-radius: 6px;
    transition: color 0.15s;
  }

  .sidebar-github:hover { color: #fff; }

  /* Content */
  .content {
    padding: 48px 48px 80px;
    min-width: 0;
  }

  .doc-section {
    padding-bottom: 64px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 64px;
  }

  .doc-section:last-of-type {
    border-bottom: none;
  }

  .doc-h1 {
    font-size: 40px;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
  }

  .doc-lead {
    font-size: 18px;
    color: var(--text-muted);
    margin-bottom: 20px;
    line-height: 1.6;
  }

  .doc-h2 {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 20px;
  }

  .doc-h3 {
    font-size: 15px;
    font-weight: 600;
    color: #ccc;
    margin: 28px 0 10px;
  }

  .doc-p {
    font-size: 14.5px;
    color: var(--text-muted);
    line-height: 1.75;
    margin-bottom: 16px;
  }

  .doc-note {
    font-size: 13px;
    color: #555;
    line-height: 1.65;
    padding: 12px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-top: 16px;
  }

  code {
    font-family: var(--mono);
    font-size: 0.88em;
    color: #a5b4fc;
    background: rgba(165,180,252,0.08);
    padding: 2px 6px;
    border-radius: 4px;
  }

  .badge-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 16px;
  }

  .badge {
    font-size: 11.5px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 100px;
    background: var(--surface-2);
    border: 1px solid var(--border-2);
    color: var(--text-muted);
  }

  .badge.green { color: #22c55e; border-color: rgba(34,197,94,0.3); background: rgba(34,197,94,0.06); }

  /* Capabilities */
  .cap-grid {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .cap-card {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: var(--surface);
    border-radius: 10px;
    border: 1px solid var(--border);
  }

  .cap-icon {
    flex-shrink: 0;
    width: 34px;
    height: 34px;
    background: var(--bg);
    border: 1px solid var(--border-2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #555;
    margin-top: 2px;
  }

  .cap-card h3 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 6px;
    color: #e2e8f0;
  }

  .cap-card p {
    font-size: 13.5px;
    color: var(--text-muted);
    line-height: 1.65;
  }

  /* Code blocks */
  .code-block {
    background: var(--surface);
    border: 1px solid var(--border-2);
    border-radius: 9px;
    padding: 14px 18px;
    margin: 10px 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .code-block.xml {
    overflow-x: auto;
  }

  .code-block pre {
    font-family: var(--mono);
    font-size: 12.5px;
    color: #888;
    line-height: 1.6;
    white-space: pre;
  }

  .code-line {
    display: flex;
    gap: 10px;
    align-items: baseline;
    font-family: var(--mono);
    font-size: 13px;
  }

  .prompt {
    color: #3b82f6;
    flex-shrink: 0;
  }

  /* State table */
  .state-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 16px;
  }

  .state-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
  }

  .state-code {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 5px;
    white-space: nowrap;
    min-width: 160px;
  }

  .state-code.normal { color: #e2e8f0; background: rgba(255,255,255,0.05); }
  .state-code.warn { color: #f59e0b; background: rgba(245,158,11,0.1); }
  .state-code.high { color: #ef4444; background: rgba(239,68,68,0.1); }
  .state-code.stress { color: #f97316; background: rgba(249,115,22,0.1); }

  .state-label {
    font-size: 13px;
    color: var(--text-muted);
  }

  /* Config table */
  .config-table {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    margin: 16px 0;
  }

  .config-row {
    display: grid;
    grid-template-columns: 140px 80px 1fr;
    gap: 12px;
    padding: 12px 16px;
    font-size: 13px;
    border-bottom: 1px solid var(--border);
    align-items: center;
  }

  .config-row:last-child { border-bottom: none; }

  .config-row.header {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-dim);
    background: var(--surface-2);
  }

  .config-row span { color: var(--text-muted); }

  /* Footer */
  .doc-footer {
    padding-top: 32px;
    text-align: center;
    font-size: 13px;
    color: var(--text-dim);
  }

  .doc-footer a { color: #555; transition: color 0.15s; }
  .doc-footer a:hover { color: #fff; }

  /* Right TOC */
  .toc {
    position: sticky;
    top: 80px;
    height: fit-content;
    padding: 48px 16px 48px 24px;
  }

  .toc-label {
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 12px;
  }

  .toc-link {
    display: block;
    font-size: 12.5px;
    color: var(--text-dim);
    padding: 5px 0;
    border-left: 2px solid transparent;
    padding-left: 10px;
    transition: color 0.15s, border-color 0.15s;
  }

  .toc-link:hover { color: #aaa; }

  .toc-link.active {
    color: #fff;
    border-left-color: #3b82f6;
  }

  @media (max-width: 1100px) {
    .toc { display: none; }
    .docs-root { grid-template-columns: 200px 1fr; }
  }

  @media (max-width: 700px) {
    .docs-root { grid-template-columns: 1fr; }
    .sidebar {
      position: static;
      height: auto;
      border-right: none;
      border-bottom: 1px solid var(--border);
      padding: 20px 0;
    }
    .content { padding: 32px 20px; }
    .state-row { flex-direction: column; align-items: flex-start; gap: 8px; }
    .state-code { min-width: unset; }
    .config-row { grid-template-columns: 1fr 60px; }
    .config-row span { display: none; }
    .config-row.header span:last-child { display: none; }
  }
</style>
