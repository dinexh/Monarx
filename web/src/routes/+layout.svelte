<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  const sections = [
    { id: 'hero', label: 'Intro' },
    { id: 'how-it-works', label: 'How It Works' },
    { id: 'features', label: 'Features' },
    { id: 'install', label: 'Install' },
  ];

  let activeSection = 'hero';
  let isDocsPage = false;

  $: isDocsPage = $page.url.pathname.startsWith('/docs');

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { if (e.isIntersecting) activeSection = e.target.id; });
      },
      { rootMargin: '-40% 0px -50% 0px' }
    );
    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  });
</script>

<svelte:head>
  <title>MacMonitor — macOS System Monitor</title>
  <meta name="description" content="Lightweight macOS menu bar app for real-time CPU, memory, and process monitoring." />
</svelte:head>

<nav class="nav">
  <a href="/" class="nav-brand">MacMonitor</a>
  <div class="nav-links">
    <a href="/#how-it-works">How it works</a>
    <a href="/#features">Features</a>
    <a href="/docs">Docs</a>
    <a href="https://github.com/dinexh/Monarx" target="_blank" rel="noopener">GitHub</a>
  </div>
</nav>

<slot />

{#if !isDocsPage}
  <nav class="section-dots" aria-label="Section navigation">
    {#each sections as s}
      <a href="#{s.id}" class="dot" class:active={activeSection === s.id} aria-label={s.label}></a>
    {/each}
  </nav>
{/if}

<style>
  .nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 40px;
    background: rgba(0,0,0,0.9);
    backdrop-filter: blur(8px);
  }

  .nav-brand {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
  }

  .nav-links {
    display: flex;
    gap: 28px;
  }

  .nav-links a {
    font-size: 13px;
    color: var(--muted);
  }

  .nav-links a:hover { color: var(--text); }

  .section-dots {
    position: fixed;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 50;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: 1px solid #444;
    background: transparent;
    display: block;
  }

  .dot.active {
    background: #fff;
    border-color: #fff;
  }

  @media (max-width: 640px) {
    .nav { padding: 16px 20px; }
    .nav-links { gap: 16px; }
    .nav-links a:not(:last-child) { display: none; }
    .section-dots { display: none; }
  }
</style>
