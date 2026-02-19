<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';

  const navLinks = [
    { href: '/#features', label: 'Features' },
    { href: '/#how-it-works', label: 'How It Works' },
    { href: '/#install', label: 'Install' },
    { href: '/docs', label: 'Docs' },
  ];

  let menuOpen = false;

  $: isDocs = $page.url.pathname.startsWith('/docs');
</script>

<svelte:head>
  <title>MacMonitor — macOS System Monitor</title>
  <meta name="description" content="Lightweight macOS menu bar app for real-time CPU, memory, and process monitoring." />
</svelte:head>

<nav class="nav" class:docs-nav={isDocs}>
  <div class="nav-inner">
    <a href="/" class="wordmark">
      <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="8" width="28" height="17" rx="3" stroke="white" stroke-width="1.8"/>
        <rect x="5" y="11" width="7" height="6" rx="1.2" fill="#3b82f6"/>
        <rect x="14" y="11" width="7" height="6" rx="1.2" fill="white" opacity="0.25"/>
        <rect x="23" y="11" width="4" height="6" rx="1.2" fill="white" opacity="0.1"/>
        <rect x="11" y="26" width="10" height="2" rx="1" fill="white" opacity="0.35"/>
      </svg>
      MacMonitor
    </a>

    <div class="nav-links desktop-only">
      {#each navLinks as { href, label }}
        <a {href} class="nav-link">{label}</a>
      {/each}
    </div>

    <div class="nav-actions">
      <a
        href="https://github.com/dinexh/Monarx"
        target="_blank"
        rel="noopener noreferrer"
        class="github-btn"
        aria-label="GitHub"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
        </svg>
        <span class="desktop-only">GitHub</span>
      </a>

      <button class="menu-toggle mobile-only" on:click={() => menuOpen = !menuOpen} aria-label="Menu">
        {#if menuOpen}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        {:else}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        {/if}
      </button>
    </div>
  </div>

  {#if menuOpen}
    <div class="mobile-menu">
      {#each navLinks as { href, label }}
        <a {href} class="mobile-link" on:click={() => menuOpen = false}>{label}</a>
      {/each}
    </div>
  {/if}
</nav>

<slot />

<style>
  .nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
  }

  .nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
  }

  .wordmark {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #fff;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .nav-links {
    display: flex;
    gap: 4px;
    flex: 1;
    justify-content: center;
  }

  .nav-link {
    padding: 6px 14px;
    font-size: 13.5px;
    color: var(--text-muted);
    border-radius: 6px;
    transition: color 0.15s, background 0.15s;
    font-weight: 500;
  }

  .nav-link:hover {
    color: #fff;
    background: var(--white-glow);
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .github-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-muted);
    border: 1px solid var(--border-2);
    border-radius: 7px;
    transition: color 0.15s, border-color 0.15s, background 0.15s;
  }

  .github-btn:hover {
    color: #fff;
    border-color: #444;
    background: var(--white-glow);
  }

  .menu-toggle {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 6px;
    border-radius: 6px;
    transition: color 0.15s;
  }

  .menu-toggle:hover { color: #fff; }

  .mobile-menu {
    display: flex;
    flex-direction: column;
    border-top: 1px solid var(--border);
    padding: 8px 0;
  }

  .mobile-link {
    padding: 12px 24px;
    font-size: 15px;
    color: var(--text-muted);
    transition: color 0.15s, background 0.15s;
  }

  .mobile-link:hover {
    color: #fff;
    background: var(--white-glow);
  }

  @media (max-width: 640px) {
    .desktop-only { display: none; }
  }

  @media (min-width: 641px) {
    .mobile-only { display: none; }
  }
</style>
