<script lang="ts">
  import { onMount } from 'svelte';
  import MenuBarMockup from '$lib/components/MenuBarMockup.svelte';
  import HowItWorks from '$lib/components/HowItWorks.svelte';

  // Scroll reveal
  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.12 }
    );

    document.querySelectorAll('.reveal, .stagger').forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  });

  const features = [
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
      title: 'Real-Time Stats',
      desc: 'CPU and memory usage sampled every 5 seconds and displayed live in your menu bar.'
    },
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/></svg>`,
      title: 'Memory Breakdown',
      desc: 'Wired, Active, Compressed, and Cached — the full macOS memory picture at a glance.'
    },
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="3"/><path d="M3 12h3m12 0h3M12 3v3m0 12v3"/></svg>`,
      title: 'Process Intelligence',
      desc: 'Top CPU and memory consumers listed in real time. Kill any process directly from the menu.'
    },
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`,
      title: 'Native Alerts',
      desc: 'macOS UserNotifications alerts when any threshold is crossed — no third-party push service.'
    },
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>`,
      title: 'Pressure Detection',
      desc: 'System memory pressure and lag risk are tracked via native sysctl — not just percentages.'
    },
    {
      icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
      title: 'Minimal Footprint',
      desc: 'Pure Python, no Electron. Lives in your menu bar with near-zero CPU overhead.'
    }
  ];

  const installSteps = [
    { cmd: 'git clone https://github.com/dinexh/Monarx.git MacMonitor', comment: '# clone the repo' },
    { cmd: 'cd MacMonitor && python3 -m venv .venv', comment: '# create virtualenv' },
    { cmd: 'source .venv/bin/activate && pip install -r requirements.txt', comment: '# install deps' },
    { cmd: 'python main.py', comment: '# launch' },
  ];

  let copied = false;
  function copyInstall() {
    const text = installSteps.map(s => s.cmd).join('\n');
    navigator.clipboard.writeText(text);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }
</script>

<svelte:head>
  <title>MacMonitor — macOS System Monitor</title>
</svelte:head>

<!-- Hero -->
<section class="hero">
  <div class="hero-bg">
    <div class="hero-grid"></div>
    <div class="hero-radial"></div>
  </div>

  <div class="hero-content">
    <div class="hero-badge reveal">
      <span class="badge-dot"></span>
      macOS menu bar · Python · Open Source
    </div>

    <h1 class="hero-title reveal">
      Your Mac,<br /><span class="title-accent">Monitored.</span>
    </h1>

    <p class="hero-sub reveal">
      A lightweight menu bar agent that shows live CPU, memory, and process stats —
      no Electron, no bloat, just clear data right where you need it.
    </p>

    <div class="hero-ctas reveal">
      <a href="#install" class="btn-primary">Get Started</a>
      <a href="/docs" class="btn-ghost">Read the Docs →</a>
    </div>

    <div class="hero-mockup reveal">
      <MenuBarMockup />
    </div>
  </div>
</section>

<!-- How It Works -->
<section id="how-it-works" class="section">
  <div class="container">
    <div class="section-label reveal">How It Works</div>
    <h2 class="section-title reveal">Four steps, always running</h2>
    <p class="section-sub reveal">MacMonitor runs a tight loop in the background — collecting, analyzing, and surfacing exactly what matters.</p>
    <HowItWorks />
  </div>
</section>

<!-- Menu bar expanded preview -->
<section class="section preview-section">
  <div class="container">
    <div class="section-label reveal">Live Preview</div>
    <h2 class="section-title reveal">Everything in the dropdown</h2>
    <p class="section-sub reveal">Click the menu bar title to expand a full system snapshot — memory breakdown, top processes, and one-click kill.</p>

    <div class="dropdown-mockup reveal">
      <div class="dm-header">
        <div class="dm-title">System Health: OK Pressure | HEALTHY</div>
      </div>
      <div class="dm-divider"></div>
      <div class="dm-row">
        <span class="dm-label">CPU</span>
        <div class="dm-bar-wrap">
          <div class="dm-bar" style="width: 43%"></div>
        </div>
        <span class="dm-val">43.0%</span>
        <span class="dm-status ok">OK</span>
      </div>
      <div class="dm-row">
        <span class="dm-label">GPU</span>
        <span class="dm-info">Activity: MODERATE</span>
      </div>
      <div class="dm-divider"></div>
      <div class="dm-row">
        <span class="dm-label">RAM</span>
        <div class="dm-bar-wrap">
          <div class="dm-bar warn" style="width: 71%"></div>
        </div>
        <span class="dm-val">71.0%</span>
        <span class="dm-status warn">WARN</span>
      </div>
      <div class="dm-mem-detail">
        <span>Wired <strong>3.20 GB</strong></span>
        <span>Active <strong>4.80 GB</strong></span>
        <span>Compressed <strong>2.10 GB</strong></span>
        <span>Cached <strong>1.50 GB</strong></span>
      </div>
      <div class="dm-divider"></div>
      <div class="dm-section-label">TOP CPU PROCESSES</div>
      {#each [['Google Chrome', '18.4%'], ['Xcode', '12.1%'], ['WindowServer', '6.7%']] as [name, pct]}
        <div class="dm-proc">
          <span class="dm-proc-name">{name}</span>
          <span class="dm-proc-val">{pct}</span>
          <button class="dm-kill">Kill</button>
        </div>
      {/each}
      <div class="dm-divider"></div>
      <div class="dm-footer">
        <span>MacMonitor v1.0.0</span>
        <span class="dm-quit">Quit</span>
      </div>
    </div>
  </div>
</section>

<!-- Features -->
<section id="features" class="section">
  <div class="container">
    <div class="section-label reveal">Features</div>
    <h2 class="section-title reveal">Built for engineers who care about their hardware</h2>

    <div class="features-grid stagger">
      {#each features as { icon, title, desc }}
        <div class="feature-card">
          <div class="feature-icon">{@html icon}</div>
          <div class="feature-text">
            <h3>{title}</h3>
            <p>{desc}</p>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Install -->
<section id="install" class="section">
  <div class="container install-container">
    <div class="install-left">
      <div class="section-label reveal">Installation</div>
      <h2 class="section-title reveal">Up in 60 seconds</h2>
      <p class="section-sub reveal">
        Requires Python 3.9+ and macOS 12+. No Homebrew, no npm, no Docker.
        Clone, install, run.
      </p>
      <ul class="req-list reveal">
        <li>macOS 12 Monterey or later</li>
        <li>Python 3.9+</li>
        <li>pip (bundled with Python)</li>
      </ul>
    </div>

    <div class="install-right reveal">
      <div class="code-block">
        <div class="code-header">
          <span class="code-title">Terminal</span>
          <button class="copy-btn" on:click={copyInstall}>
            {#if copied}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Copied!
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              Copy
            {/if}
          </button>
        </div>
        <div class="code-body">
          {#each installSteps as { cmd, comment }, i}
            <div class="code-line">
              <span class="code-prompt">$</span>
              <span class="code-cmd">{cmd}</span>
              {#if i === 0}<span class="code-comment">&nbsp;&nbsp;{comment}</span>{/if}
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
        <rect x="2" y="8" width="28" height="17" rx="3" stroke="white" stroke-width="1.8" opacity="0.6"/>
        <rect x="5" y="11" width="7" height="6" rx="1.2" fill="#3b82f6" opacity="0.7"/>
        <rect x="11" y="26" width="10" height="2" rx="1" fill="white" opacity="0.25"/>
      </svg>
      <span>MacMonitor</span>
    </div>
    <p class="footer-copy">© 2026 MacMonitor · MIT License · Built for macOS</p>
    <div class="footer-links">
      <a href="/docs">Docs</a>
      <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">GitHub</a>
      <a href="https://github.com/dinexh/Monarx/issues" target="_blank" rel="noopener">Issues</a>
    </div>
  </div>
</footer>

<style>
  /* ── Hero ─────────────────────────────────────── */
  .hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 100px 24px 80px;
  }

  .hero-bg {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .hero-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse 80% 80% at 50% 30%, black 30%, transparent 100%);
  }

  .hero-radial {
    position: absolute;
    top: -20%;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    border-radius: 50%;
    animation: pulse-glow 6s ease-in-out infinite;
  }

  @keyframes pulse-glow {
    0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1); }
    50% { opacity: 1; transform: translateX(-50%) scale(1.08); }
  }

  .hero-content {
    position: relative;
    max-width: 780px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 28px;
  }

  .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: var(--surface-2);
    border: 1px solid var(--border-2);
    border-radius: 100px;
    font-size: 12.5px;
    color: var(--text-muted);
    letter-spacing: 0.02em;
    font-weight: 500;
  }

  .badge-dot {
    width: 7px;
    height: 7px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    animation: blink 2s ease-in-out infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .hero-title {
    font-size: clamp(52px, 9vw, 92px);
    font-weight: 700;
    line-height: 1.0;
    letter-spacing: -0.04em;
    color: #fff;
  }

  .title-accent {
    background: linear-gradient(135deg, #fff 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-sub {
    font-size: clamp(15px, 2.2vw, 18px);
    color: var(--text-muted);
    max-width: 540px;
    line-height: 1.7;
  }

  .hero-ctas {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .btn-primary {
    padding: 12px 28px;
    background: #fff;
    color: #000;
    font-weight: 600;
    font-size: 14px;
    border-radius: 8px;
    transition: opacity 0.15s, transform 0.15s;
    letter-spacing: -0.01em;
  }

  .btn-primary:hover { opacity: 0.88; transform: translateY(-1px); }

  .btn-ghost {
    padding: 12px 24px;
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 500;
    border: 1px solid var(--border-2);
    border-radius: 8px;
    transition: color 0.15s, border-color 0.15s, background 0.15s;
  }

  .btn-ghost:hover {
    color: #fff;
    border-color: #444;
    background: var(--white-glow);
  }

  .hero-mockup {
    width: 100%;
    max-width: 680px;
    margin-top: 8px;
  }

  /* ── Sections ─────────────────────────────────── */
  .section {
    padding: 100px 24px;
    position: relative;
  }

  .container {
    max-width: 1080px;
    margin: 0 auto;
  }

  .section-label {
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 16px;
  }

  .section-title {
    font-size: clamp(28px, 4.5vw, 44px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 16px;
    max-width: 600px;
  }

  .section-sub {
    font-size: 16px;
    color: var(--text-muted);
    max-width: 500px;
    line-height: 1.7;
    margin-bottom: 56px;
  }

  /* ── Dropdown Preview ─────────────────────────── */
  .preview-section {
    background: linear-gradient(180deg, transparent, rgba(59,130,246,0.03) 50%, transparent);
  }

  .dropdown-mockup {
    max-width: 520px;
    margin: 0 auto;
    background: #0d0d0d;
    border: 1px solid var(--border-2);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04), 0 40px 80px rgba(0,0,0,0.8);
    font-family: var(--mono);
    font-size: 13px;
  }

  .dm-header {
    padding: 14px 18px 10px;
    background: var(--surface);
  }

  .dm-title {
    color: #888;
    font-size: 11px;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .dm-divider {
    height: 1px;
    background: var(--border);
    margin: 4px 0;
  }

  .dm-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px;
  }

  .dm-label {
    color: #888;
    width: 40px;
    font-size: 11.5px;
    flex-shrink: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .dm-bar-wrap {
    flex: 1;
    height: 6px;
    background: var(--border-2);
    border-radius: 3px;
    overflow: hidden;
  }

  .dm-bar {
    height: 100%;
    background: #3b82f6;
    border-radius: 3px;
    transition: width 1s ease;
  }

  .dm-bar.warn { background: #f59e0b; }

  .dm-val {
    color: #ccc;
    font-size: 12px;
    width: 42px;
    text-align: right;
    flex-shrink: 0;
  }

  .dm-status {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 4px;
    flex-shrink: 0;
  }

  .dm-status.ok { color: #22c55e; background: rgba(34,197,94,0.12); }
  .dm-status.warn { color: #f59e0b; background: rgba(245,158,11,0.12); }

  .dm-info {
    color: #666;
    font-size: 12px;
  }

  .dm-mem-detail {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    padding: 4px 18px 10px;
  }

  .dm-mem-detail span {
    font-size: 11.5px;
    color: #555;
  }

  .dm-mem-detail strong {
    color: #999;
    font-weight: 500;
  }

  .dm-section-label {
    padding: 8px 18px 4px;
    font-size: 10px;
    color: #555;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .dm-proc {
    display: flex;
    align-items: center;
    padding: 6px 18px;
    gap: 12px;
  }

  .dm-proc-name {
    flex: 1;
    font-size: 12.5px;
    color: #ccc;
  }

  .dm-proc-val {
    font-size: 12px;
    color: #888;
    width: 44px;
    text-align: right;
  }

  .dm-kill {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    color: #ef4444;
    font-size: 10.5px;
    padding: 2px 10px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s;
    font-family: var(--font);
  }

  .dm-kill:hover { background: rgba(239,68,68,0.2); }

  .dm-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 18px 14px;
    color: #444;
    font-size: 11.5px;
  }

  .dm-quit {
    color: #ef4444;
    cursor: pointer;
    opacity: 0.7;
  }

  /* ── Features ─────────────────────────────────── */
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
  }

  .feature-card {
    display: flex;
    gap: 18px;
    padding: 28px 26px;
    background: var(--surface);
    transition: background 0.2s;
  }

  .feature-card:hover { background: var(--surface-2); }

  .feature-icon {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: var(--bg);
    border: 1px solid var(--border-2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    transition: color 0.2s, border-color 0.2s;
  }

  .feature-card:hover .feature-icon {
    color: #fff;
    border-color: #333;
  }

  .feature-text h3 {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 6px;
    color: #e8e8e8;
  }

  .feature-text p {
    font-size: 13.5px;
    color: var(--text-muted);
    line-height: 1.65;
  }

  /* ── Install ──────────────────────────────────── */
  .install-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 64px;
    align-items: start;
  }

  .req-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .req-list li {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: var(--text-muted);
  }

  .req-list li::before {
    content: '';
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #3b82f6;
    flex-shrink: 0;
  }

  .code-block {
    background: var(--surface);
    border: 1px solid var(--border-2);
    border-radius: 12px;
    overflow: hidden;
  }

  .code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
    background: var(--surface-2);
  }

  .code-title {
    font-size: 12px;
    color: var(--text-dim);
    font-family: var(--mono);
    letter-spacing: 0.04em;
  }

  .copy-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    background: none;
    border: 1px solid var(--border-2);
    color: var(--text-muted);
    font-size: 11.5px;
    padding: 4px 10px;
    border-radius: 5px;
    cursor: pointer;
    transition: color 0.15s, border-color 0.15s;
    font-family: var(--font);
  }

  .copy-btn:hover { color: #fff; border-color: #444; }

  .code-body {
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .code-line {
    display: flex;
    align-items: baseline;
    gap: 10px;
    flex-wrap: wrap;
  }

  .code-prompt {
    color: #3b82f6;
    font-family: var(--mono);
    font-size: 13px;
    flex-shrink: 0;
  }

  .code-cmd {
    font-family: var(--mono);
    font-size: 13px;
    color: #e2e8f0;
    word-break: break-all;
  }

  .code-comment {
    font-family: var(--mono);
    font-size: 12px;
    color: #444;
  }

  /* ── Footer ───────────────────────────────────── */
  .footer {
    border-top: 1px solid var(--border);
    padding: 40px 24px;
  }

  .footer-inner {
    max-width: 1080px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    flex-wrap: wrap;
  }

  .footer-brand {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #555;
  }

  .footer-copy {
    font-size: 12.5px;
    color: var(--text-dim);
  }

  .footer-links {
    display: flex;
    gap: 20px;
  }

  .footer-links a {
    font-size: 13px;
    color: var(--text-dim);
    transition: color 0.15s;
  }

  .footer-links a:hover { color: #fff; }

  @media (max-width: 768px) {
    .install-container {
      grid-template-columns: 1fr;
      gap: 40px;
    }

    .footer-inner {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
