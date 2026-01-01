"use client";

import React, { useState, useEffect } from "react";
import { Github, Sun, Moon } from "lucide-react";
import Link from "next/link";

export default function DocsPage() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add('dark');
      html.style.colorScheme = 'dark';
    } else {
      html.classList.remove('dark');
      html.style.colorScheme = 'light';
    }
  }, [isDark]);

  return (
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white transition-colors duration-300 flex flex-col lg:flex-row">
      {/* Sidebar */}
      <aside className="w-full lg:w-72 border-b lg:border-r border-black/10 dark:border-white/5 h-auto lg:h-screen lg:sticky lg:top-0 p-8 bg-white dark:bg-black">
        <div className="mb-12">
          <Link href="/" className="text-xl font-medium hover:opacity-70 transition-opacity">Monarx</Link>
        </div>
        
        <nav className="space-y-1">
          <SidebarLink href="#overview" label="Overview" active />
          <SidebarLink href="#capabilities" label="Capabilities" />
          <SidebarLink href="#installation" label="Installation" />
          <SidebarLink href="#usage" label="Usage" />
          <SidebarLink href="#configuration" label="Configuration" />
          <SidebarLink href="#auto-start" label="Auto-Start" />
        </nav>

        <div className="mt-12 hidden lg:block">
          <h4 className="text-[10px] font-bold uppercase tracking-[0.2em] text-black/30 dark:text-white/30 mb-4 px-3">Resources</h4>
          <a 
            href="https://github.com/dinexh/Monarx" 
            className="block px-3 py-2 text-sm text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white transition-colors rounded-lg hover:bg-black/5 dark:hover:bg-white/5"
          >
            GitHub Repo
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-6 lg:px-12 py-12 lg:py-24">
        <Link href="/" className="lg:hidden flex items-center gap-2 text-black/60 dark:text-white/60 text-sm mb-12 hover:text-black dark:hover:text-white transition-colors">
          ← Back to Home
        </Link>

        <header className="mb-16">
          <div className="text-xs text-black/30 dark:text-white/30 uppercase tracking-widest mb-4">Documentation</div>
          <h1 className="text-5xl font-light mb-6 tracking-tight">Monarx</h1>
          <p className="text-xl text-black/60 dark:text-white/40 leading-relaxed">
            Comprehensive guide to the intelligent macOS system monitoring agent. 
            Track performance, identify memory pressure, and monitor top processes.
          </p>
        </header>

        <Section id="overview" title="Overview">
          <p>
            Monarx is a lightweight, real-time system monitoring application designed exclusively for macOS. 
            It hooks into native macOS kernel interfaces and system APIs to provide deep visibility into 
            CPU usage, detailed memory breakdown, and system health alerts directly in your menu bar.
          </p>
        </Section>

        <Section id="capabilities" title="Core Capabilities">
          <div className="grid sm:grid-cols-2 gap-6 mt-8">
            <CapabilityItem 
              title="Native Menu Bar UI" 
              description="Monitor all vital system stats from a clean, non-intrusive menu bar dropdown." 
            />
            <CapabilityItem 
              title="Memory Pressure" 
              description="Identify Wired, Active, Compressed, and Cached memory states with 1-second updates." 
            />
            <CapabilityItem 
              title="Process Intelligence" 
              description="See exactly which processes are consuming CPU and memory with the ability to kill them." 
            />
            <CapabilityItem 
              title="Threat Detection" 
              description="Stay informed with native notifications for high resource usage and lag risks." 
            />
          </div>
        </Section>

        <Section id="installation" title="Installation">
          <p className="mb-6">
            Monarx requires Python 3.9+ and can be installed via pip. 
            It uses `rumps` for the menu bar and `psutil` for resource tracking.
          </p>
          <div className="bg-black dark:bg-[#0d0d0d] rounded-xl border border-black/10 dark:border-white/5 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2 bg-black/10 dark:bg-white/5 text-[10px] font-mono text-black/30 dark:text-white/30">
              Terminal
            </div>
            <pre className="p-6 text-sm font-mono text-blue-500 dark:text-blue-400 leading-relaxed overflow-x-auto">
{`# Clone the repository
git clone https://github.com/dinexh/Monarx.git
cd Monarx

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install psutil rumps pyobjc`}
            </pre>
          </div>
        </Section>

        <Section id="usage" title="Usage">
          <p className="mb-6">
            Run the application using the entry point script. 
            The app will automatically initialize and appear in your macOS menu bar.
          </p>
          <div className="bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/5 p-6 rounded-lg">
            <code className="text-sm font-mono text-black dark:text-white">python main.py</code>
          </div>
        </Section>

        <Section id="configuration" title="Configuration">
          <p className="mb-6">
            Thresholds and intervals can be configured in `core/config.py`. 
            These settings determine when notifications are triggered.
          </p>
          <div className="bg-black dark:bg-[#0d0d0d] rounded-xl border border-black/10 dark:border-white/5 overflow-hidden">
             <div className="flex items-center gap-2 px-4 py-2 bg-black/10 dark:bg-white/5 text-[10px] font-mono text-black/30 dark:text-white/30 uppercase tracking-widest">
              Python Config
            </div>
            <pre className="p-6 text-sm font-mono text-black/60 dark:text-white/60 leading-relaxed overflow-x-auto">
{`CPU_LIMIT = 85      # Alert when CPU exceeds 85%
MEM_LIMIT = 80      # Alert when Memory exceeds 80%
SWAP_LIMIT = 20     # Alert when Swap exceeds 20%
CHECK_EVERY = 5     # Refresh interval (seconds)
COOLDOWN = 120      # Cooldown for repeat alerts`}
            </pre>
          </div>
        </Section>

        <Section id="auto-start" title="Auto-Start (macOS)">
          <p className="mb-6">
            To have Monarx start automatically on login, create a LaunchAgent plist file.
          </p>
          <div className="bg-black dark:bg-[#0d0d0d] rounded-xl border border-black/10 dark:border-white/5 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2 bg-black/10 dark:bg-white/5 text-[10px] font-mono text-black/30 dark:text-white/30">
               com.monarx.plist
            </div>
            <pre className="p-6 text-[13px] font-mono text-black/40 dark:text-white/40 leading-relaxed overflow-x-auto">
{`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monarx</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/.venv/bin/python</string>
        <string>/path/to/Monarx/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>`}
            </pre>
          </div>
        </Section>

        <footer className="mt-24 pt-12 border-t border-black/10 dark:border-white/5 flex items-center justify-between text-black/40 dark:text-white/40 text-sm">
          <p>© 2026 Monarx. Open Source Software.</p>
          <div className="flex gap-6">
            <a href="https://github.com/dinexh/Monarx" className="hover:text-black dark:hover:text-white transition-colors">GitHub</a>
            <Link href="/" className="hover:text-black dark:hover:text-white transition-colors">Home</Link>
          </div>
        </footer>
      </main>

      {/* Right Sidebar (On this page) */}
      <aside className="hidden xl:block w-64 h-screen sticky top-0 p-12 border-l border-black/10 dark:border-white/5 bg-white dark:bg-black">
        <h4 className="text-[10px] font-bold uppercase tracking-[0.2em] text-black/30 dark:text-white/30 mb-6">On this page</h4>
        <nav className="space-y-4">
          <OnPageLink href="#overview" label="Overview" />
          <OnPageLink href="#capabilities" label="Capabilities" />
          <OnPageLink href="#installation" label="Installation" />
          <OnPageLink href="#usage" label="Usage" />
          <OnPageLink href="#configuration" label="Configuration" />
          <OnPageLink href="#auto-start" label="Auto-Start" />
        </nav>
      </aside>

      {/* Theme Toggle - Fixed at bottom */}
      <button
        onClick={() => setIsDark(!isDark)}
        className="fixed bottom-8 right-8 w-14 h-14 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center shadow-lg hover:scale-110 active:scale-95 transition-all z-50 border-2 border-black/10 dark:border-white/10"
        aria-label="Toggle theme"
      >
        {isDark ? <Sun size={22} /> : <Moon size={22} />}
      </button>
    </div>
  );
}

function Section({ id, title, children }: { id: string, title: string, children: React.ReactNode }) {
  return (
    <section id={id} className="mb-20 scroll-mt-32">
      <h2 className="text-2xl font-medium mb-6">{title}</h2>
      <div className="text-black/60 dark:text-white/60 leading-relaxed space-y-4">
        {children}
      </div>
    </section>
  );
}

function SidebarLink({ href, label, active = false }: { href: string, label: string, active?: boolean }) {
  return (
    <Link 
      href={href} 
      className={`block px-3 py-2 text-sm rounded-lg transition-all ${
        active 
        ? "bg-black/10 dark:bg-white/10 text-black dark:text-white font-medium" 
        : "text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5"
      }`}
    >
      {label}
    </Link>
  );
}

function OnPageLink({ href, label }: { href: string, label: string }) {
  return (
    <Link href={href} className="block text-xs text-black/40 dark:text-white/40 hover:text-black dark:hover:text-white transition-colors">
      {label}
    </Link>
  );
}

function CapabilityItem({ title, description }: { title: string, description: string }) {
  return (
    <div className="bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/5 p-6 rounded-lg">
      <h4 className="text-sm font-medium mb-2">{title}</h4>
      <p className="text-xs text-black/60 dark:text-white/60 leading-relaxed">{description}</p>
    </div>
  );
}
