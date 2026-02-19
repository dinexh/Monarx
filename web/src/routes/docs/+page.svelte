<script lang="ts">
  import { onMount } from 'svelte';

  const sections = [
    { id: 'overview',      label: 'Overview'      },
    { id: 'capabilities',  label: 'Capabilities'  },
    { id: 'installation',  label: 'Installation'  },
    { id: 'usage',         label: 'Usage'         },
    { id: 'configuration', label: 'Configuration' },
    { id: 'auto-start',    label: 'Auto-Start'    },
  ];

  let active = 'overview';

  // ── Config interactive table ──────────────────────
  const configVars = [
    { name: 'CPU_LIMIT',   default: '85',  unit: '%',   desc: 'Alert when CPU usage reaches this threshold.' },
    { name: 'MEM_LIMIT',   default: '80',  unit: '%',   desc: 'Alert when RAM usage reaches this threshold.' },
    { name: 'SWAP_LIMIT',  default: '20',  unit: '%',   desc: 'Alert when swap usage reaches this threshold.' },
    { name: 'CHECK_EVERY', default: '5',   unit: 's',   desc: 'How often metrics are sampled. Lower = more responsive, higher CPU cost.' },
    { name: 'COOLDOWN',    default: '120', unit: 's',   desc: 'Minimum time between repeated alerts for the same metric.' },
  ];

  let selectedConfig: typeof configVars[0] | null = null;

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { if (e.isIntersecting) active = e.target.id; });
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
  <meta name="description" content="MacMonitor documentation." />
</svelte:head>

<div class="docs-root">
  <!-- Sidebar -->
  <aside class="sidebar">
    <p class="sidebar-label">Documentation</p>
    <nav>
      {#each sections as s}
        <a href="#{s.id}" class="sidebar-link" class:active={active === s.id}>{s.label}</a>
      {/each}
    </nav>
    <div class="sidebar-sep"></div>
    <a href="/" class="sidebar-back">← MacMonitor</a>
    <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener" class="sidebar-gh">GitHub ↗</a>
  </aside>

  <!-- Content -->
  <main class="content">

    <section id="overview" class="doc-section">
      <h1>MacMonitor</h1>
      <p class="lead">A lightweight macOS menu bar application for real-time system monitoring.</p>
      <p>
        MacMonitor lives in your menu bar and shows live CPU and memory usage at a glance.
        It uses native macOS APIs — <code>vm_stat</code>, <code>sysctl</code>, and the
        UserNotifications framework — for accurate, low-overhead telemetry with no background daemon required.
      </p>
      <div class="tag-row">
        <span class="tag">Python 3.9+</span>
        <span class="tag">macOS 12+</span>
        <span class="tag">MIT License</span>
        <span class="tag green">v1.0.0</span>
      </div>
    </section>

    <section id="capabilities" class="doc-section">
      <h2>Capabilities</h2>

      <div class="cap-list">
        <div class="cap-item">
          <h3>Native Menu Bar UI</h3>
          <p>
            The title updates every 5 seconds: <code>C:XX% M:XX%</code>. When pressure or usage is elevated,
            it switches to <code>WARN</code>, <code>HIGH</code>, or <code>STRESS</code> prefix automatically.
            No app window, no Dock icon.
          </p>
        </div>

        <div class="cap-item">
          <h3>Memory Breakdown</h3>
          <p>
            Reads <code>vm_stat</code> and <code>memory_pressure</code> to decompose RAM into four categories:
            <strong>Wired</strong>, <strong>Active</strong>, <strong>Compressed</strong>, and <strong>Cached</strong>.
            Flags lag risk when Compressed memory exceeds Active.
          </p>
        </div>

        <div class="cap-item">
          <h3>Process Intelligence</h3>
          <p>
            Top 5 CPU and memory consumers listed in real time.
            Kill any process directly from the dropdown without opening Activity Monitor.
            Chrome, Electron, Slack, and Discord are auto-tagged as GPU-heavy.
          </p>
        </div>

        <div class="cap-item">
          <h3>Native Alerts</h3>
          <p>
            Threshold breaches trigger <strong>UserNotifications</strong> alerts — the same system used by Calendar and Mail.
            Alerts use a stable identifier so they replace each other in-place rather than stacking.
            120-second cooldown per metric.
          </p>
        </div>
      </div>
    </section>

    <section id="installation" class="doc-section">
      <h2>Installation</h2>
      <p>Requires Python 3.9+ and macOS 12 Monterey or later.</p>

      <h3>1. Clone</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> git clone https://github.com/dinexh/Monarx.git MacMonitor</div>
        <div class="code-line"><span class="p">$</span> cd MacMonitor</div>
      </div>

      <h3>2. Virtual environment</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> python3 -m venv .venv</div>
        <div class="code-line"><span class="p">$</span> source .venv/bin/activate</div>
      </div>

      <h3>3. Dependencies</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> pip install -r requirements.txt</div>
      </div>
      <p class="note">Installs: <code>psutil</code> · <code>rumps</code> · <code>pyobjc-framework-Cocoa</code> · <code>pyobjc-framework-UserNotifications</code> · <code>pytest</code></p>
    </section>

    <section id="usage" class="doc-section">
      <h2>Usage</h2>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> python main.py</div>
      </div>
      <p>MacMonitor appears in your menu bar immediately as <code>C:XX% M:XX%</code>. Click it to open the dropdown.</p>

      <h3>Menu bar states</h3>
      <div class="state-list">
        <div class="state-row">
          <code class="state normal">C:43% M:71%</code>
          <span>All metrics within configured thresholds</span>
        </div>
        <div class="state-row">
          <code class="state warn">WARN C:58% M:74%</code>
          <span>Memory pressure at WARN level</span>
        </div>
        <div class="state-row">
          <code class="state high">HIGH C:91% M:83%</code>
          <span>Memory pressure is HIGH</span>
        </div>
        <div class="state-row">
          <code class="state stress">STRESS C:35% M:76%</code>
          <span>Compressed memory exceeds Active (lag risk)</span>
        </div>
      </div>
    </section>

    <section id="configuration" class="doc-section">
      <h2>Configuration</h2>
      <p>
        Change thresholds at runtime via <strong>Settings → Change Thresholds</strong> in the dropdown,
        or edit <code>core/config.py</code> directly.
        Values persist in <code>~/Library/Application Support/MacMonitor/config.json</code>.
      </p>

      <p class="section-hint">Click a row to see details.</p>

      <!-- Interactive config table -->
      <div class="config-table">
        {#each configVars as v}
          <button
            class="config-row"
            class:active={selectedConfig?.name === v.name}
            on:click={() => selectedConfig = selectedConfig?.name === v.name ? null : v}
          >
            <code class="config-name">{v.name}</code>
            <span class="config-val">{v.default}{v.unit}</span>
            <span class="config-arrow">{selectedConfig?.name === v.name ? '↑' : '↓'}</span>
          </button>
          {#if selectedConfig?.name === v.name}
            <div class="config-detail">
              <p>{v.desc}</p>
              <div class="code-block">
                <div class="code-line">
                  <span class="p">#</span>
                  <span>core/config.py</span>
                </div>
                <div class="code-line">
                  <span class="p" style="color:#888">{v.name}</span>
                  <span style="color:#555"> = </span>
                  <span style="color:#e2e8f0">{v.default}</span>
                  <span style="color:#555">  # {v.desc.split('.')[0].toLowerCase()}</span>
                </div>
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </section>

    <section id="auto-start" class="doc-section">
      <h2>Auto-Start on Login</h2>
      <p>
        Create a LaunchAgent plist to start MacMonitor automatically at login.
        Replace <code>/path/to/MacMonitor</code> with your actual clone path.
      </p>

      <h3>1. Create the plist</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> nano ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <div class="code-block">
        <pre class="xml-block">{`<?xml version="1.0" encoding="UTF-8"?>
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
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
</dict>
</plist>`}</pre>
      </div>

      <h3>2. Load the agent</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> launchctl load ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <h3>Unload</h3>
      <div class="code-block">
        <div class="code-line"><span class="p">$</span> launchctl unload ~/Library/LaunchAgents/com.macmonitor.plist</div>
      </div>

      <h3>Log files</h3>
      <p>MacMonitor writes logs to <code>~/Library/Logs/MacMonitor/macmonitor.log</code>.
      Open them from the menu via <strong>View Logs</strong>.</p>
    </section>

    <div class="doc-footer">
      <p>Built with [<a href="https://www.python.org" target="_blank" rel="noopener">Python</a>]. View [<a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">source</a>].</p>
      <p>Made by [<a href="https://dineshkorukonda.in" target="_blank" rel="noopener">Dinesh Korukonda</a>].</p>
    </div>
  </main>

  <!-- Right TOC dots -->
  <nav class="toc-dots" aria-label="On this page">
    {#each sections as s}
      <a href="#{s.id}" class="toc-dot" class:active={active === s.id} title={s.label}></a>
    {/each}
  </nav>
</div>

<style>
  .docs-root {
    display: grid;
    grid-template-columns: 200px 1fr 36px;
    min-height: 100vh;
    padding-top: 60px;
    max-width: 1160px;
    margin: 0 auto;
  }

  /* ── Sidebar ─────────────────────────────────────── */
  .sidebar {
    position: sticky;
    top: 60px;
    height: calc(100vh - 60px);
    overflow-y: auto;
    padding: 40px 24px 40px 40px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    border-right: 1px solid var(--border);
  }

  .sidebar-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 10px;
  }

  .sidebar-link {
    display: block;
    font-size: 13.5px;
    color: var(--muted);
    padding: 6px 10px;
    border-radius: 4px;
    border-left: 2px solid transparent;
  }

  .sidebar-link:hover { color: var(--text); }

  .sidebar-link.active {
    color: var(--text);
    border-left-color: var(--text);
    background: var(--surface);
  }

  .sidebar-sep {
    height: 1px;
    background: var(--border);
    margin: 20px 0 16px;
  }

  .sidebar-back, .sidebar-gh {
    font-size: 12.5px;
    color: var(--dim);
    padding: 4px 10px;
  }

  .sidebar-back:hover, .sidebar-gh:hover { color: var(--muted); }

  /* ── Content ─────────────────────────────────────── */
  .content {
    padding: 48px 56px 80px 56px;
    min-width: 0;
  }

  .doc-section {
    padding-bottom: 64px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 64px;
  }

  .doc-section:last-of-type { border-bottom: none; }

  h1 {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 12px;
    color: var(--text);
  }

  h2 {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 16px;
    color: var(--text);
  }

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: #ccc;
    margin: 28px 0 10px;
  }

  .lead {
    font-size: 17px;
    color: var(--muted);
    margin-bottom: 20px;
    line-height: 1.65;
  }

  p {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.75;
    margin-bottom: 16px;
  }

  .note {
    font-size: 12.5px;
    color: var(--dim);
    margin-top: 8px;
    margin-bottom: 0;
  }

  .section-hint {
    font-size: 13px;
    color: var(--dim);
    margin-bottom: 12px;
  }

  code {
    font-family: var(--mono);
    font-size: 0.88em;
    color: #999;
    background: #0d0d0d;
    border: 1px solid var(--border);
    padding: 1px 6px;
    border-radius: 3px;
  }

  strong { color: #ccc; font-weight: 500; }

  .tag-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 16px;
  }

  .tag {
    font-size: 11.5px;
    padding: 3px 10px;
    border: 1px solid var(--border);
    border-radius: 3px;
    color: var(--dim);
  }

  .tag.green { color: var(--muted); }

  /* ── Capabilities ────────────────────────────────── */
  .cap-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .cap-item {
    padding: 20px 0;
    border-bottom: 1px solid var(--border);
  }

  .cap-item:last-child { border-bottom: none; }

  .cap-item h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 8px;
  }

  .cap-item p {
    font-size: 13.5px;
    margin: 0;
  }

  /* ── Code blocks ─────────────────────────────────── */
  .code-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 14px 16px;
    margin: 10px 0;
    display: flex;
    flex-direction: column;
    gap: 7px;
  }

  .code-line {
    display: flex;
    gap: 10px;
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
    align-items: baseline;
    flex-wrap: wrap;
  }

  .p { color: var(--dim); flex-shrink: 0; }

  .xml-block {
    font-family: var(--mono);
    font-size: 12px;
    color: #666;
    line-height: 1.65;
    white-space: pre;
    overflow-x: auto;
  }

  /* ── States ──────────────────────────────────────── */
  .state-list {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 16px;
    border: 1px solid var(--border);
    border-radius: 5px;
    overflow: hidden;
  }

  .state-row {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 13.5px;
    color: var(--muted);
  }

  .state-row:last-child { border-bottom: none; }

  .state {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 600;
    width: 180px;
    flex-shrink: 0;
    border: none;
    background: none;
    padding: 0;
  }

  .state.normal { color: var(--text); }
  .state.warn   { color: var(--muted); }
  .state.high   { color: var(--muted); }
  .state.stress { color: var(--muted); }

  /* ── Config table ────────────────────────────────── */
  .config-table {
    border: 1px solid var(--border);
    border-radius: 5px;
    overflow: hidden;
    margin: 16px 0;
  }

  .config-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
    width: 100%;
    background: none;
    border-left: none;
    border-right: none;
    border-top: none;
    cursor: pointer;
    text-align: left;
  }

  .config-row:last-of-type { border-bottom: none; }
  .config-row:hover { background: var(--surface); }
  .config-row.active { background: var(--surface); border-bottom-color: var(--border); }

  .config-name {
    font-family: var(--mono);
    font-size: 13px;
    color: #aaa;
    background: none;
    border: none;
    padding: 0;
    width: 130px;
    flex-shrink: 0;
  }

  .config-val {
    font-family: var(--mono);
    font-size: 13px;
    color: var(--text);
    flex: 1;
  }

  .config-arrow {
    font-size: 12px;
    color: var(--dim);
  }

  .config-detail {
    padding: 16px 18px 20px;
    border-bottom: 1px solid var(--border);
    background: #050505;
  }

  .config-detail p {
    font-size: 13px;
    margin-bottom: 12px;
  }

  /* ── Footer ──────────────────────────────────────── */
  .doc-footer {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-top: 16px;
  }

  .doc-footer p { font-size: 13px; color: var(--dim); }
  .doc-footer a { color: var(--dim); border-bottom: 1px solid #222; }
  .doc-footer a:hover { color: var(--muted); }

  /* ── Right TOC dots ──────────────────────────────── */
  .toc-dots {
    position: sticky;
    top: 50vh;
    height: fit-content;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-top: 48px;
    align-items: center;
  }

  .toc-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    border: 1px solid #333;
    background: transparent;
    display: block;
  }

  .toc-dot.active {
    background: var(--text);
    border-color: var(--text);
  }

  /* ── Responsive ──────────────────────────────────── */
  @media (max-width: 900px) {
    .toc-dots { display: none; }
    .docs-root { grid-template-columns: 180px 1fr; }
  }

  @media (max-width: 640px) {
    .docs-root { grid-template-columns: 1fr; padding-top: 60px; }
    .sidebar {
      position: static;
      height: auto;
      border-right: none;
      border-bottom: 1px solid var(--border);
      padding: 24px 20px;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 4px;
      overflow: visible;
    }
    .sidebar-label, .sidebar-sep, .sidebar-back, .sidebar-gh { display: none; }
    .sidebar-link { padding: 5px 10px; font-size: 12.5px; }
    .content { padding: 32px 20px; }
    .state { width: 140px; }
  }
</style>
