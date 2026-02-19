<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  // Cycles through realistic stat snapshots
  const snapshots = [
    { cpu: 43, mem: 71, label: 'C:43% M:71%', state: 'normal' },
    { cpu: 58, mem: 74, label: 'WARN C:58% M:74%', state: 'warn' },
    { cpu: 91, mem: 83, label: 'HIGH C:91% M:83%', state: 'high' },
    { cpu: 22, mem: 68, label: 'C:22% M:68%', state: 'normal' },
    { cpu: 35, mem: 76, label: 'STRESS C:35% M:76%', state: 'stress' },
  ];

  let idx = 0;
  let snap = snapshots[0];
  let interval: ReturnType<typeof setInterval>;

  onMount(() => {
    interval = setInterval(() => {
      idx = (idx + 1) % snapshots.length;
      snap = snapshots[idx];
    }, 2500);
  });

  onDestroy(() => clearInterval(interval));

  function barFill(pct: number) {
    const filled = Math.round(pct / 100 * 10);
    return '■'.repeat(filled) + '□'.repeat(10 - filled);
  }
</script>

<div class="mockup-shell">
  <!-- macOS menu bar strip -->
  <div class="menubar">
    <div class="menubar-left">
      <span class="apple-icon">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="white" opacity="0.7">
          <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
        </svg>
      </span>
      <span class="menubar-item">File</span>
      <span class="menubar-item">Edit</span>
      <span class="menubar-item">View</span>
    </div>

    <div class="menubar-right">
      <span class="menubar-item faint">Thu 14:32</span>
      <span
        class="monitor-title"
        class:warn={snap.state === 'warn'}
        class:high={snap.state === 'high'}
        class:stress={snap.state === 'stress'}
      >
        {snap.label}
      </span>
    </div>
  </div>

  <!-- Expanded dropdown -->
  <div class="dropdown">
    <div class="drop-header">
      System Health:
      <span class:green={snap.state === 'normal'} class:amber={snap.state === 'warn'} class:red={snap.state === 'high' || snap.state === 'stress'}>
        {snap.state === 'normal' ? 'OK Pressure' : snap.state === 'warn' ? 'WARN Pressure' : 'HIGH Pressure'}
      </span>
      |
      <span class:green={snap.state === 'normal'} class:red={snap.state === 'stress'}>
        {snap.state === 'stress' ? 'STRESSED' : 'HEALTHY'}
      </span>
    </div>
    <div class="drop-divider"></div>

    <div class="drop-row">
      <span class="drop-lbl">CPU</span>
      <span class="drop-bar mono">[{barFill(snap.cpu)}]</span>
      <span class="drop-val">{snap.cpu}.0%</span>
    </div>
    <div class="drop-row">
      <span class="drop-lbl">GPU</span>
      <span class="drop-info">Activity: {snap.cpu > 60 ? 'HEAVY' : snap.cpu > 30 ? 'MODERATE' : 'IDLE'}</span>
    </div>
    <div class="drop-divider"></div>
    <div class="drop-row">
      <span class="drop-lbl">RAM</span>
      <span class="drop-bar mono">[{barFill(snap.mem)}]</span>
      <span class="drop-val">{snap.mem}.0%</span>
    </div>
    <div class="drop-indent">Wired: 3.20 GB · Active: {(snap.mem * 0.16).toFixed(2)} GB · Compressed: 2.10 GB</div>
    <div class="drop-divider"></div>
    <div class="drop-section">TOP CPU PROCESSES</div>
    <div class="drop-row proc"><span class="proc-name">Google Chrome</span><span class="proc-val">{Math.max(5, Math.round(snap.cpu * 0.4))}.1%</span></div>
    <div class="drop-row proc"><span class="proc-name">Xcode</span><span class="proc-val">{Math.max(3, Math.round(snap.cpu * 0.25))}.8%</span></div>
    <div class="drop-row proc"><span class="proc-name">WindowServer</span><span class="proc-val">{Math.max(2, Math.round(snap.cpu * 0.14))}.2%</span></div>
    <div class="drop-divider"></div>
    <div class="drop-footer">
      <span>MacMonitor v1.0.0</span>
      <span class="quit-text">Quit</span>
    </div>
  </div>
</div>

<style>
  .mockup-shell {
    border-radius: 12px;
    overflow: hidden;
    box-shadow:
      0 0 0 1px rgba(255,255,255,0.06),
      0 30px 60px rgba(0,0,0,0.7),
      0 0 80px rgba(59,130,246,0.06);
    background: #0d0d0d;
    border: 1px solid #1e1e1e;
    font-size: 12.5px;
    max-width: 620px;
    margin: 0 auto;
    animation: float 5s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }

  /* Menu bar */
  .menubar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(20,20,20,0.98);
    padding: 0 14px;
    height: 28px;
    border-bottom: 1px solid #1a1a1a;
  }

  .menubar-left, .menubar-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .apple-icon { display: flex; align-items: center; }

  .menubar-item {
    font-size: 12px;
    color: rgba(255,255,255,0.7);
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 500;
  }

  .faint { color: rgba(255,255,255,0.35) !important; font-size: 11.5px; }

  .monitor-title {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 11.5px;
    font-weight: 600;
    color: #e2e8f0;
    transition: color 0.5s ease;
    padding: 2px 8px;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
    letter-spacing: 0.02em;
  }

  .monitor-title.warn { color: #f59e0b; background: rgba(245,158,11,0.1); }
  .monitor-title.high { color: #ef4444; background: rgba(239,68,68,0.1); }
  .monitor-title.stress { color: #f97316; background: rgba(249,115,22,0.1); }

  /* Dropdown */
  .dropdown {
    padding: 0;
    background: #0d0d0d;
    font-family: 'SF Mono', 'Fira Code', monospace;
  }

  .drop-header {
    padding: 10px 16px;
    font-size: 10.5px;
    color: #666;
    letter-spacing: 0.02em;
  }

  .drop-header .green { color: #22c55e; }
  .drop-header .amber { color: #f59e0b; }
  .drop-header .red { color: #ef4444; }

  .drop-divider {
    height: 1px;
    background: #1a1a1a;
    margin: 2px 0;
  }

  .drop-row {
    display: flex;
    align-items: center;
    padding: 6px 16px;
    gap: 10px;
  }

  .drop-row.proc { gap: 0; }

  .drop-lbl {
    color: #555;
    width: 36px;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    flex-shrink: 0;
  }

  .drop-bar {
    color: #3b82f6;
    font-size: 11px;
    flex: 1;
    transition: all 0.6s ease;
  }

  .drop-val {
    color: #999;
    font-size: 11.5px;
    width: 40px;
    text-align: right;
  }

  .drop-info {
    color: #555;
    font-size: 11px;
  }

  .drop-indent {
    padding: 3px 16px 8px 52px;
    font-size: 10.5px;
    color: #444;
    line-height: 1.6;
  }

  .drop-section {
    padding: 7px 16px 4px;
    font-size: 10px;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .proc-name {
    flex: 1;
    font-size: 11.5px;
    color: #ccc;
  }

  .proc-val {
    font-size: 11px;
    color: #666;
  }

  .drop-footer {
    display: flex;
    justify-content: space-between;
    padding: 9px 16px 12px;
    font-size: 11px;
    color: #3a3a3a;
  }

  .quit-text { color: #ef4444; opacity: 0.6; }

  .mono { font-family: inherit; }
</style>
