<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  // ── App state snapshots ───────────────────────────
  const snapshots = [
    {
      label: 'C:20% M:70%',
      health: 'OK Pressure | HEALTHY',
      cpu: 20.8, mem: 70.3, swap: 17.5,
      memTotal: 8.0,
      wired: 1.44, active: 2.32, compressed: 1.30, cached: 2.31,
      cpuStatus: 'OK', gpuActivity: 'IDLE',
      cpuProcs: [
        { name: '2.1.47', pct: '31.7%' },
        { name: 'com.apple.WebKit....GPU [GPU]', pct: '7.3%' },
        { name: 'IntelligencePlatformComp...', pct: '6.3%' },
        { name: 'ControlCenter', pct: '5.8%' },
        { name: 'Safari', pct: '5.1%' },
      ],
      memProcs: [
        { name: 'com.appl....WebContent [GPU]', pct: '5.3%' },
        { name: '2.1.47', pct: '3.9%' },
        { name: 'Safari', pct: '1.6%' },
        { name: 'com.appl....WebContent [GPU]', pct: '1.2%' },
        { name: 'ghostty', pct: '1.1%' },
      ],
    },
    {
      label: 'WARN C:58% M:74%',
      health: 'WARN Pressure | HEALTHY',
      cpu: 58.2, mem: 74.1, swap: 19.0,
      memTotal: 8.0,
      wired: 2.10, active: 3.40, compressed: 3.80, cached: 1.20,
      cpuStatus: 'WARN', gpuActivity: 'MODERATE',
      cpuProcs: [
        { name: 'Xcode', pct: '24.1%' },
        { name: 'com.apple.WebKit....GPU [GPU]', pct: '18.5%' },
        { name: 'node', pct: '9.2%' },
        { name: 'Simulator', pct: '7.8%' },
        { name: 'Safari', pct: '4.3%' },
      ],
      memProcs: [
        { name: 'Xcode', pct: '12.4%' },
        { name: 'Simulator', pct: '8.1%' },
        { name: 'com.appl....WebContent [GPU]', pct: '6.9%' },
        { name: 'node', pct: '4.2%' },
        { name: 'Safari', pct: '2.1%' },
      ],
    },
    {
      label: 'HIGH C:91% M:83%',
      health: 'HIGH Pressure | STRESSED',
      cpu: 91.2, mem: 83.0, swap: 22.0,
      memTotal: 8.0,
      wired: 2.80, active: 2.10, compressed: 4.90, cached: 0.60,
      cpuStatus: 'HIGH', gpuActivity: 'HEAVY',
      cpuProcs: [
        { name: 'Xcode', pct: '41.3%' },
        { name: 'Simulator', pct: '22.7%' },
        { name: 'com.apple.WebKit....GPU [GPU]', pct: '15.1%' },
        { name: 'node', pct: '12.4%' },
        { name: 'kernel_task', pct: '6.1%' },
      ],
      memProcs: [
        { name: 'Xcode', pct: '18.3%' },
        { name: 'Simulator', pct: '14.2%' },
        { name: 'com.appl....WebContent [GPU]', pct: '8.7%' },
        { name: 'node', pct: '6.4%' },
        { name: 'kernel_task', pct: '3.2%' },
      ],
    },
  ];

  let snapIdx = 0;
  let snap = snapshots[0];
  let autoInterval: ReturnType<typeof setInterval>;
  let isAuto = true;
  let transitioning = false;
  let stepFading = false;

  $: healthColor = snap.cpuStatus === 'HIGH' ? '#7a3a3a'
                 : snap.cpuStatus === 'WARN' ? '#7a6530'
                 : 'var(--muted)';

  function bar(pct: number): string {
    const filled = Math.min(10, Math.round(pct / 100 * 10));
    return '[' + '■'.repeat(filled) + '□'.repeat(10 - filled) + ']';
  }

  // Expanded process row
  let expandedCpuIdx: number | null = null;
  let expandedMemIdx: number | null = null;

  function toggleCpu(i: number) {
    expandedCpuIdx = expandedCpuIdx === i ? null : i;
    expandedMemIdx = null;
  }
  function toggleMem(i: number) {
    expandedMemIdx = expandedMemIdx === i ? null : i;
    expandedCpuIdx = null;
  }

  function setSnap(i: number) {
    if (i === snapIdx && !isAuto) return;
    clearInterval(autoInterval);
    isAuto = false;
    transitioning = true;
    setTimeout(() => {
      snapIdx = i;
      snap = snapshots[i];
      expandedCpuIdx = null;
      expandedMemIdx = null;
      transitioning = false;
    }, 180);
  }

  function startAuto() {
    isAuto = true;
    autoInterval = setInterval(() => {
      transitioning = true;
      setTimeout(() => {
        snapIdx = (snapIdx + 1) % snapshots.length;
        snap = snapshots[snapIdx];
        expandedCpuIdx = null;
        expandedMemIdx = null;
        transitioning = false;
      }, 180);
    }, 3000);
  }

  function setStep(i: number) {
    if (i === activeStep) return;
    stepFading = true;
    setTimeout(() => {
      activeStep = i;
      stepFading = false;
    }, 150);
  }

  // ── How It Works ─────────────────────────────────
  const steps = [
    {
      num: '01', title: 'Collect',
      desc: 'Every 5 seconds, native macOS APIs are called to sample the full system state.',
      code: `vm_stat | grep "Pages"
sysctl -n vm.memory_pressure
psutil.cpu_percent(interval=None)
psutil.process_iter(['pid','name','cpu_percent'])`
    },
    {
      num: '02', title: 'Analyze',
      desc: 'Raw values are structured into a stats dict. Memory is decomposed. Lag risk is flagged when Compressed > Active.',
      code: `stats = {
  'cpu': 43.2, 'mem': 71.0,
  'pressure': 'OK', 'lag_risk': False,
  'macos_mem': {
    'wired': 3.2, 'active': 4.8,
    'compressed': 2.1, 'cached': 1.5
  }
}`
    },
    {
      num: '03', title: 'Alert',
      desc: 'Threshold breaches fire native macOS UserNotifications with a 120-second cooldown per metric.',
      code: `notify("High CPU", "CPU at 91.2%",
       identifier="macmonitor.high-cpu")
# Stable ID → replaces existing alert
# Falls back to osascript if needed`
    },
    {
      num: '04', title: 'Display',
      desc: 'The menu bar title updates every tick. Dropdown shows the full breakdown with live process data.',
      code: `# Normal:  C:43% M:71%
# Warning: WARN C:58% M:74%
# High:    HIGH C:91% M:83%
# Stress:  STRESS C:35% M:76%`
    },
  ];
  let activeStep = 0;

  // ── Features tabs ────────────────────────────────
  const featureTabs = [
    {
      label: 'Menu Bar',
      content: `macmonitor ~/

$ python main.py

C:43% M:71%   ← live in your menu bar

States:
  C:XX% M:XX%          normal
  WARN C:XX% M:XX%     pressure warn
  HIGH C:XX% M:XX%     pressure high
  STRESS C:XX% M:XX%   lag risk detected

Refreshes every 5 seconds. Click to expand.`
    },
    {
      label: 'Memory',
      content: `RAM  [■■■■■■■□□□]  71.0% of 16.0 GB

  Wired:       3.20 GB
  Active:      4.80 GB
  Compressed:  2.10 GB   ← high if > Active
  Cached:      1.50 GB

Swap [■■□□□□□□□□]  18.0%

Memory pressure: OK
Lag risk:        False`
    },
    {
      label: 'Processes',
      content: `TOP CPU PROCESSES:
  Google Chrome:           18.4%  [GPU]
  Xcode:                   12.1%
  WindowServer:             6.7%  [GPU]
  kernel_task:              4.2%
  mds_stores:               3.1%  [Spotlight]

TOP MEMORY PROCESSES:
  Xcode:                    8.2%
  Google Chrome:            6.5%  [GPU]
  Simulator:                4.1%

Each row → Kill Process / Activity Monitor`
    },
    {
      label: 'Alerts',
      content: `[UNNotifications] High CPU
  body:       "CPU at 91.2%"
  id:         macmonitor.high-cpu
  cooldown:   120s

[UNNotifications] Memory Pressure
  body:       "Status: HIGH"
  id:         macmonitor.pressure

[UNNotifications] Lag Risk
  body:       "Compressed > Active Memory"
  id:         macmonitor.lag-risk`
    },
  ];
  let activeTab = 0;

  // ── Install copy ─────────────────────────────────
  const installCmd = `git clone https://github.com/dinexh/Monarx.git MacMonitor
cd MacMonitor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py`;

  let copied = false;
  function copyCmd() {
    navigator.clipboard.writeText(installCmd);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }

  onMount(() => {
    startAuto();

    // Section entrance animations
    const animEls = document.querySelectorAll('.section-animate');
    const sectionObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('visible');
            sectionObs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.08 }
    );
    animEls.forEach((el) => sectionObs.observe(el));

    return () => sectionObs.disconnect();
  });
  onDestroy(() => clearInterval(autoInterval));
</script>

<svelte:head><title>MacMonitor — macOS System Monitor</title></svelte:head>

<!-- ── Hero ─────────────────────────────────────── -->
<section id="hero" class="section hero-section">
  <div class="container">

    <h1 class="hero-title">MacMonitor</h1>

    <p class="hero-desc">
      A lightweight macOS menu bar app built with
      [<a href="https://www.python.org" target="_blank" rel="noopener">Python</a>]
      and [<a href="https://github.com/jaredks/rumps" target="_blank" rel="noopener">rumps</a>].
      Real-time CPU, memory, and process monitoring — no Electron, no Dock icon, no bloat.
    </p>

    <p class="hero-links">
      View the [<a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">source code</a>]
      or try the [<a href="#features">live demo</a>] below.
      <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener" class="gh-btn">★ Star on GitHub</a>
    </p>

    <!-- Interactive app replica -->
    <div class="app-demo">
      <div class="demo-topbar">
        <span class="demo-path">MacMonitor — live preview<span class="blink-cursor">_</span></span>
        <div class="demo-controls">
          {#each snapshots as s, i}
            <button
              class="ctrl-btn"
              class:active={snapIdx === i && !isAuto}
              on:click={() => setSnap(i)}
            >{s.label}</button>
          {/each}
          <button
            class="ctrl-btn"
            class:active={isAuto}
            on:click={() => { clearInterval(autoInterval); startAuto(); }}
          >auto</button>
        </div>
      </div>

      {#key snapIdx}
        {#if isAuto}
          <div class="progress-bar"></div>
        {/if}
      {/key}

      <div class="dropdown-replica" class:fading={transitioning}>
        <!-- Health -->
        <div class="dr-row health-row" style="color: {healthColor}">System Health: {snap.health}</div>
        <div class="dr-divider"></div>

        <!-- CPU -->
        <div class="dr-row">CPU {bar(snap.cpu)} {snap.cpu}%  [{snap.cpuStatus}]</div>
        <div class="dr-row dim-row">GPU Activity: {snap.gpuActivity}</div>
        <div class="dr-divider"></div>

        <!-- RAM -->
        <div class="dr-row">RAM {bar(snap.mem)} {snap.mem}% of {snap.memTotal} GB</div>
        <div class="dr-indent">Wired:       {snap.wired.toFixed(2)} GB</div>
        <div class="dr-indent">Active:      {snap.active.toFixed(2)} GB</div>
        <div class="dr-indent">Compressed:  {snap.compressed.toFixed(2)} GB{snap.compressed > snap.active ? '   ← HIGH' : ''}</div>
        <div class="dr-indent">Cached:      {snap.cached.toFixed(2)} GB</div>
        <div class="dr-row">Swap {bar(snap.swap)} {snap.swap}%</div>
        <div class="dr-divider"></div>

        <!-- Settings -->
        <div class="dr-section">SETTINGS</div>
        <div class="dr-row indent-row">Thresholds: CPU 85% | MEM 80% | SWAP 20%</div>
        <div class="dr-divider"></div>

        <!-- CPU Processes -->
        <div class="dr-section">TOP CPU PROCESSES:</div>
        {#each snap.cpuProcs as p, i}
          <button class="dr-proc" on:click={() => toggleCpu(i)}>
            <span class="proc-name">{p.name}:</span>
            <span class="proc-pct">{p.pct}</span>
            <span class="proc-arrow">{expandedCpuIdx === i ? '↓' : '›'}</span>
          </button>
          {#if expandedCpuIdx === i}
            <div class="proc-actions">
              <button class="proc-action-btn">Kill Process</button>
              <button class="proc-action-btn">Open Activity Monitor</button>
            </div>
          {/if}
        {/each}
        <div class="dr-divider"></div>

        <!-- Memory Processes -->
        <div class="dr-section">TOP MEMORY PROCESSES:</div>
        {#each snap.memProcs as p, i}
          <button class="dr-proc" on:click={() => toggleMem(i)}>
            <span class="proc-name">{p.name}:</span>
            <span class="proc-pct">{p.pct}</span>
            <span class="proc-arrow">{expandedMemIdx === i ? '↓' : '›'}</span>
          </button>
          {#if expandedMemIdx === i}
            <div class="proc-actions">
              <button class="proc-action-btn">Kill Process</button>
              <button class="proc-action-btn">Open Activity Monitor</button>
            </div>
          {/if}
        {/each}
        <div class="dr-divider"></div>

        <!-- Footer actions -->
        <div class="dr-row">REFRESH</div>
        <div class="dr-row">VIEW LOGS</div>
        <div class="dr-row dim-row">MacMonitor v1.0.0</div>
        <div class="dr-divider"></div>
        <div class="dr-row">QUIT</div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat"><span class="stat-num">5s</span><span class="stat-lbl">Refresh Rate</span></div>
      <div class="stat"><span class="stat-num">6</span><span class="stat-lbl">Metrics Tracked</span></div>
      <div class="stat"><span class="stat-num">120s</span><span class="stat-lbl">Alert Cooldown</span></div>
      <div class="stat"><span class="stat-num">5</span><span class="stat-lbl">Top Processes</span></div>
    </div>

  </div>
</section>

<!-- ── How It Works ──────────────────────────────── -->
<section id="how-it-works" class="section section-animate">
  <div class="container">
    <h2 class="section-heading">How It Works</h2>
    <p class="section-sub">
      Data flows through four logical stages every 5 seconds.
      Click each stage to see details.
    </p>

    <div class="arch-layout">
      <div class="arch-list">
        {#each steps as step, i}
          <button
            class="arch-item"
            class:active={activeStep === i}
            on:click={() => setStep(i)}
          >
            <span class="arch-num">{step.num}</span>
            <span class="arch-title">{step.title}</span>
          </button>
        {/each}
      </div>

      <div class="arch-detail" class:fading={stepFading}>
        <h3 class="arch-detail-title">{steps[activeStep].title}</h3>
        <p class="arch-detail-desc">{steps[activeStep].desc}</p>
        <div class="code-panel">
          <pre>{steps[activeStep].code}</pre>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ── Features ──────────────────────────────────── -->
<section id="features" class="section section-animate">
  <div class="container">
    <h2 class="section-heading">Features</h2>
    <p class="section-sub">
      Switch between views to see what each part of MacMonitor exposes.
    </p>

    <div class="tab-bar">
      {#each featureTabs as tab, i}
        <button
          class="tab-btn"
          class:active={activeTab === i}
          on:click={() => (activeTab = i)}
        >{tab.label}</button>
      {/each}
    </div>

    <div class="terminal-panel">
      <div class="terminal-bar">macmonitor · {featureTabs[activeTab].label.toLowerCase()}</div>
      <div class="terminal-body">
        <pre class="t-pre">{featureTabs[activeTab].content}</pre>
      </div>
    </div>

    <div class="feature-pairs">
      <div class="fp-item"><strong>No Electron</strong> — <span>pure Python, near-zero overhead</span></div>
      <div class="fp-item"><strong>Native alerts</strong> — <span>UserNotifications, not osascript banners</span></div>
      <div class="fp-item"><strong>Process kill</strong> — <span>SIGTERM any process from the menu</span></div>
      <div class="fp-item"><strong>Lag detection</strong> — <span>flags when Compressed memory exceeds Active</span></div>
      <div class="fp-item"><strong>GPU tagging</strong> — <span>Chrome, Electron, Slack auto-labelled</span></div>
      <div class="fp-item"><strong>Persistent config</strong> — <span>thresholds saved to ~/Library/Application Support</span></div>
    </div>
  </div>
</section>

<!-- ── Install ───────────────────────────────────── -->
<section id="install" class="section section-animate">
  <div class="container">
    <h2 class="section-heading">Get started</h2>
    <p class="section-sub">Requires Python 3.9+ and macOS 12 Monterey or later.</p>

    <div class="terminal-panel">
      <div class="terminal-bar terminal-bar-actions">
        <span>Terminal</span>
        <button class="copy-btn" on:click={copyCmd}>{copied ? '✓ copied' : 'copy'}</button>
      </div>
      <div class="terminal-body">
        {#each installCmd.split('\n') as line}
          <div class="t-line">
            <span class="t-prompt">$</span>
            <span class="t-cmd">{line}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="install-note">
      Auto-start on login via LaunchAgent — see the [<a href="/docs#auto-start">docs</a>].
      Logs at <code>~/Library/Logs/MacMonitor/macmonitor.log</code>.
    </p>
  </div>
</section>

<!-- ── Footer ────────────────────────────────────── -->
<footer class="footer">
  <div class="container">
    <p>Built with [<a href="https://www.python.org" target="_blank" rel="noopener">Python</a>] and [<a href="https://github.com/jaredks/rumps" target="_blank" rel="noopener">rumps</a>]. View [<a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">source</a>].</p>
    <p>Made by [<a href="https://dineshkorukonda.in" target="_blank" rel="noopener">Dinesh Korukonda</a>].</p>
  </div>
</footer>

<style>
  .container { max-width: 900px; margin: 0 auto; padding: 0 40px; }
  .section { padding: 100px 0; }
  .hero-section { padding-top: 140px; padding-bottom: 80px; }

  /* ── Hero ──────────────────────────────────────── */
  .hero-title {
    font-size: 48px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 28px;
  }

  .hero-desc {
    font-size: 16px;
    color: var(--muted);
    line-height: 1.75;
    max-width: 620px;
    margin-bottom: 16px;
  }

  .hero-desc a,
  .hero-links a:not(.gh-btn) {
    color: var(--muted);
    border-bottom: 1px solid #333;
  }

  .hero-desc a:hover,
  .hero-links a:not(.gh-btn):hover {
    color: var(--text);
    border-color: #666;
  }

  .hero-links {
    font-size: 15px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 40px;
  }

  .gh-btn {
    padding: 6px 14px;
    border: 1px solid #333;
    border-radius: 4px;
    font-size: 13px;
    color: var(--text) !important;
    border-bottom: 1px solid #333 !important;
  }

  .gh-btn:hover { border-color: #555 !important; background: var(--surface); }

  /* ── App demo replica ──────────────────────────── */
  .app-demo {
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--surface);
    overflow: hidden;
    margin-bottom: 48px;
  }

  .demo-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    background: #0a0a0a;
    flex-wrap: wrap;
    gap: 10px;
  }

  .demo-path {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--dim);
  }

  .blink-cursor {
    animation: blink 1s step-end infinite;
    margin-left: 1px;
    color: var(--dim);
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }

  /* Auto-rotate progress bar */
  .progress-bar {
    height: 1px;
    background: #111;
    position: relative;
    overflow: hidden;
  }

  .progress-bar::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    background: #3a3a3a;
    width: 0;
    animation: progress-grow 2.9s linear forwards;
  }

  @keyframes progress-grow {
    to { width: 100%; }
  }

  .demo-controls {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .ctrl-btn {
    background: none;
    border: 1px solid #242424;
    color: var(--dim);
    font-family: var(--mono);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 3px;
    cursor: pointer;
  }

  .ctrl-btn:hover { border-color: #444; color: var(--muted); }
  .ctrl-btn.active { border-color: #666; color: var(--text); background: #111; }

  /* Dropdown replica - monospace, matches real app */
  .dropdown-replica {
    font-family: var(--mono);
    font-size: 13px;
    max-height: 500px;
    overflow-y: auto;
    transition: opacity 0.18s ease;
  }

  .dropdown-replica.fading { opacity: 0; }

  .dr-row {
    padding: 6px 18px;
    color: var(--text);
    white-space: pre;
    line-height: 1.5;
  }

  .health-row { color: var(--muted); font-size: 12px; padding-top: 10px; }
  .dim-row    { color: var(--muted); }
  .indent-row { padding-left: 32px; }

  .dr-indent {
    padding: 2px 18px 2px 36px;
    font-family: var(--mono);
    font-size: 12.5px;
    color: var(--muted);
    white-space: pre;
  }

  .dr-divider {
    height: 1px;
    background: var(--border);
    margin: 4px 0;
  }

  .dr-section {
    padding: 8px 18px 4px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--dim);
    letter-spacing: 0.04em;
  }

  .dr-proc {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 5px 18px;
    background: none;
    border: none;
    cursor: pointer;
    text-align: left;
    gap: 0;
    font-family: var(--mono);
    font-size: 13px;
  }

  .dr-proc:hover { background: #111; }

  .proc-name {
    flex: 1;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 340px;
  }

  .proc-pct  { color: var(--muted); width: 50px; text-align: right; }
  .proc-arrow { color: var(--dim); width: 20px; text-align: right; }

  .proc-actions {
    display: flex;
    gap: 8px;
    padding: 6px 18px 8px 36px;
    border-bottom: 1px solid var(--border);
  }

  .proc-action-btn {
    background: none;
    border: 1px solid #2a2a2a;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 11.5px;
    padding: 4px 12px;
    border-radius: 3px;
    cursor: pointer;
  }

  .proc-action-btn:hover { border-color: #444; color: var(--text); }

  /* ── Stats row ─────────────────────────────────── */
  .stats-row {
    display: flex;
    gap: 48px;
    flex-wrap: wrap;
  }

  .stat { display: flex; flex-direction: column; gap: 6px; }

  .stat-num {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .stat-lbl {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--dim);
  }

  /* ── Section typography ─────────────────────────── */
  .section-heading {
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 12px;
  }

  .section-sub {
    font-size: 15px;
    color: var(--muted);
    margin-bottom: 40px;
    max-width: 520px;
    line-height: 1.7;
  }

  /* ── Architecture ───────────────────────────────── */
  .arch-layout {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 20px;
    align-items: start;
  }

  .arch-list { display: flex; flex-direction: column; gap: 2px; }

  .arch-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 14px;
    background: none;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-align: left;
    width: 100%;
  }

  .arch-item:hover { background: var(--surface); }
  .arch-item.active { background: var(--surface); }

  .arch-num {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--dim);
    width: 24px;
    flex-shrink: 0;
  }

  .arch-item.active .arch-num { color: var(--muted); }

  .arch-title { font-size: 14px; color: var(--muted); }
  .arch-item.active .arch-title { color: var(--text); }

  .arch-detail {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 24px;
    background: var(--surface);
    transition: opacity 0.15s ease;
  }

  .arch-detail.fading { opacity: 0; }

  .arch-detail-title { font-size: 18px; font-weight: 600; margin-bottom: 10px; }

  .arch-detail-desc {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.7;
    margin-bottom: 20px;
  }

  .code-panel {
    background: #060606;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 18px;
  }

  .code-panel pre {
    font-family: var(--mono);
    font-size: 12.5px;
    color: var(--muted);
    line-height: 1.7;
    white-space: pre;
    overflow-x: auto;
  }

  /* ── Tabs ───────────────────────────────────────── */
  .tab-bar { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }

  .tab-btn {
    padding: 6px 16px;
    border: 1px solid #2a2a2a;
    background: none;
    color: var(--muted);
    font-size: 13px;
    font-family: var(--font);
    border-radius: 4px;
    cursor: pointer;
  }

  .tab-btn:hover { border-color: #444; color: var(--text); }
  .tab-btn.active { background: var(--text); color: var(--bg); border-color: var(--text); }

  /* ── Terminal panel (features / install) ────────── */
  .terminal-panel {
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--surface);
    overflow: hidden;
    margin-bottom: 32px;
  }

  .terminal-bar {
    padding: 10px 16px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--dim);
    border-bottom: 1px solid var(--border);
    background: #0a0a0a;
  }

  .terminal-bar-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .terminal-body {
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .t-pre {
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
    line-height: 1.7;
    white-space: pre;
    overflow-x: auto;
  }

  .t-line {
    display: flex;
    align-items: baseline;
    gap: 10px;
    font-family: var(--mono);
    font-size: 13px;
  }

  .t-prompt { color: var(--dim); flex-shrink: 0; }
  .t-cmd    { color: #ccc; }

  .copy-btn {
    background: none;
    border: 1px solid #2a2a2a;
    color: var(--dim);
    font-family: var(--mono);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 3px;
    cursor: pointer;
  }

  .copy-btn:hover { border-color: #444; color: var(--muted); }

  /* ── Feature pairs ──────────────────────────────── */
  .feature-pairs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    margin-top: 16px;
  }

  .fp-item {
    padding: 14px 0;
    font-size: 14px;
    border-bottom: 1px solid var(--border);
    color: var(--muted);
    line-height: 1.5;
    padding-right: 24px;
  }

  .fp-item:nth-last-child(-n+2) { border-bottom: none; }
  .fp-item strong { color: var(--text); font-weight: 500; }

  /* ── Install note ───────────────────────────────── */
  .install-note {
    font-size: 13.5px;
    color: var(--dim);
    line-height: 1.7;
    margin-top: -16px;
  }

  .install-note a { color: var(--dim); border-bottom: 1px solid #2a2a2a; }
  .install-note a:hover { color: var(--muted); }
  .install-note code { font-family: var(--mono); font-size: 12.5px; color: #555; }

  /* ── Footer ─────────────────────────────────────── */
  .footer { border-top: 1px solid var(--border); padding: 40px 0; }
  .footer .container { display: flex; flex-direction: column; gap: 6px; }
  .footer p { font-size: 13px; color: var(--dim); }
  .footer a { color: var(--dim); border-bottom: 1px solid #222; }
  .footer a:hover { color: var(--muted); }

  /* ── Responsive ─────────────────────────────────── */
  @media (max-width: 700px) {
    .container { padding: 0 20px; }
    .section { padding: 70px 0; }
    .hero-section { padding-top: 100px; }
    .hero-title { font-size: 32px; }
    .arch-layout { grid-template-columns: 1fr; }
    .arch-list { flex-direction: row; flex-wrap: wrap; }
    .arch-item { flex: 1; min-width: 80px; }
    .feature-pairs { grid-template-columns: 1fr; }
    .fp-item:nth-last-child(-n+2) { border-bottom: 1px solid var(--border); }
    .fp-item:last-child { border-bottom: none; }
    .stats-row { gap: 32px; }
    .proc-name { max-width: 180px; }
  }
</style>
