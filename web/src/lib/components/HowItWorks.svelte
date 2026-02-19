<script lang="ts">
  import { onMount } from 'svelte';

  const steps = [
    {
      number: '01',
      title: 'Collect',
      desc: 'Every 5 seconds, MacMonitor calls macOS-native APIs — vm_stat, sysctl, memory_pressure, and psutil — to sample CPU, memory, swap, and process data.',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
    },
    {
      number: '02',
      title: 'Analyze',
      desc: 'Values are compared against your configured thresholds. Memory is decomposed into Wired, Active, Compressed, and Cached. GPU-heavy processes are tagged automatically.',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35M11 8v3l2 2"/></svg>`
    },
    {
      number: '03',
      title: 'Alert',
      desc: 'When a threshold is crossed, a native macOS UserNotifications alert fires — with a 120-second cooldown so you\'re never spammed.',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`
    },
    {
      number: '04',
      title: 'Display',
      desc: 'The menu bar title updates instantly: C:XX% M:XX% in normal mode, or WARN / HIGH / STRESS prefixed when pressure is elevated. The full dropdown gives the complete picture.',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>`
    }
  ];

  let activeStep = -1;
  let container: HTMLElement;

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          // Animate steps in sequence
          steps.forEach((_, i) => {
            setTimeout(() => { activeStep = i; }, i * 200);
          });
        }
      },
      { threshold: 0.2 }
    );
    if (container) observer.observe(container);
    return () => observer.disconnect();
  });
</script>

<div class="hiw" bind:this={container}>
  {#each steps as step, i}
    <div class="step" class:active={activeStep >= i}>
      <div class="step-num">{step.number}</div>
      <div class="step-connector" class:last={i === steps.length - 1}></div>
      <div class="step-content">
        <div class="step-icon">{@html step.icon}</div>
        <h3 class="step-title">{step.title}</h3>
        <p class="step-desc">{step.desc}</p>
      </div>
    </div>
  {/each}
</div>

<style>
  .hiw {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    position: relative;
    margin-top: 16px;
  }

  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
  }

  .step.active {
    opacity: 1;
    transform: translateY(0);
  }

  .step-num {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 1px solid #222;
    background: #0d0d0d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    font-family: var(--mono);
    color: #444;
    letter-spacing: 0.05em;
    position: relative;
    z-index: 1;
    transition: border-color 0.4s, color 0.4s, background 0.4s, box-shadow 0.4s;
  }

  .step.active .step-num {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(59,130,246,0.08);
    box-shadow: 0 0 20px rgba(59,130,246,0.15);
  }

  .step-connector {
    width: 100%;
    height: 1px;
    background: #1a1a1a;
    position: absolute;
    top: 24px;
    left: 50%;
    z-index: 0;
    transition: background 0.4s;
  }

  .step-connector.last {
    display: none;
  }

  .step.active .step-connector {
    background: linear-gradient(90deg, #3b82f6, #1a1a1a);
  }

  .step-content {
    padding: 24px 16px 0;
  }

  .step-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    color: #555;
    transition: color 0.4s;
  }

  .step.active .step-icon { color: #888; }

  .step-title {
    font-size: 15px;
    font-weight: 600;
    color: #555;
    margin-bottom: 10px;
    transition: color 0.4s;
    letter-spacing: -0.01em;
  }

  .step.active .step-title { color: #e8e8e8; }

  .step-desc {
    font-size: 13px;
    color: #444;
    line-height: 1.65;
    transition: color 0.4s;
  }

  .step.active .step-desc { color: #666; }

  @media (max-width: 768px) {
    .hiw {
      grid-template-columns: 1fr;
      gap: 32px;
      padding-left: 16px;
    }

    .step {
      flex-direction: row;
      align-items: flex-start;
      text-align: left;
      gap: 20px;
    }

    .step-connector { display: none; }
    .step-content { padding: 0; }
    .step-num { flex-shrink: 0; }
    .step-icon { margin: 0 0 10px; justify-content: flex-start; }
  }
</style>
