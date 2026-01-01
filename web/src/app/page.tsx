"use client";

import React, { useState, useEffect } from "react";
import { Github, Sun, Moon } from "lucide-react";

export default function LandingPage() {
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
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white transition-colors duration-300">
      {/* Simple Header */}
      <header className="fixed top-0 w-full z-50 bg-white/95 dark:bg-black/95 backdrop-blur-md border-b border-black/10 dark:border-white/5">
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <a href="/" className="text-lg font-medium hover:opacity-70 transition-opacity">Monarx</a>
          <div className="flex items-center gap-6">
            <a href="#features" className="text-sm text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white transition-colors hidden md:block">Features</a>
            <a href="#technical" className="text-sm text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white transition-colors hidden md:block">Technical</a>
            <a href="/docs" className="text-sm text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white transition-colors hidden md:block">Docs</a>
            <a href="https://github.com/dinexh/Monarx" className="text-black/60 dark:text-white/60 hover:text-black dark:hover:text-white transition-colors">
              <Github size={18} />
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-24 px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-light tracking-tight mb-6 leading-tight">
            macOS System Monitor
          </h1>
          <p className="text-xl text-black/60 dark:text-white/40 mb-12 leading-relaxed max-w-2xl mx-auto">
            Real-time resource monitoring and process intelligence in your menu bar. 
            Lightweight, native, and unobtrusive.
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <a 
              href="https://github.com/dinexh/Monarx" 
              className="px-6 py-3 bg-black dark:bg-white text-white dark:text-black hover:opacity-90 transition-opacity text-sm font-medium"
            >
              View on GitHub
            </a>
            <a 
              href="/docs" 
              className="px-6 py-3 border border-black/10 dark:border-white/10 hover:border-black/20 dark:hover:border-white/20 transition-colors text-sm font-medium"
            >
              Documentation
            </a>
          </div>
        </div>
      </section>

      {/* Menu Bar Preview */}
      <section className="py-16 px-8 border-t border-black/10 dark:border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 text-center">
            <div className="text-xs text-black/30 dark:text-white/30 uppercase tracking-widest mb-2">Menu Bar Interface</div>
            <div className="text-sm text-black/60 dark:text-white/60">Live system stats accessible from your macOS menu bar</div>
          </div>
          
          {/* macOS Menu Bar Mockup based on reference images */}
          <div className="bg-[#1a1a1a] border border-white/10 rounded-lg overflow-hidden max-w-4xl mx-auto">
            {/* macOS Menu Bar */}
            <div className="bg-[#2a2a2a] px-4 py-2.5 flex items-center justify-between border-b border-white/10">
              <div className="flex items-center gap-4 text-xs text-white/60">
                <span className="font-medium text-white/80">Monarx</span>
                <span>File</span>
                <span>Edit</span>
                <span>View</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-xs font-medium text-white">STRESS! | CPU 18% | MEM 80%</div>
                <div className="w-5 h-5 rounded bg-blue-500/30 flex items-center justify-center">
                  <div className="w-3 h-3 rounded bg-blue-500"></div>
                </div>
              </div>
            </div>
            
            {/* Menu Bar Dropdown - Based on reference images */}
            <div className="p-6 bg-black">
              <div className="mb-4 pb-3 border-b border-white/5">
                <div className="text-sm text-white/40 mb-1">System Health</div>
                <div className="text-base font-medium">NORMAL Pressure | STRESSED</div>
              </div>
              
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/60">CPU Load</span>
                  <span className="text-white font-medium">17.9% (NORMAL)</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/60">GPU Activity</span>
                  <span className="text-white font-medium">IDLE</span>
                </div>
              </div>
              
              <div className="mb-4 pb-4 border-b border-white/5">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-white/60">RAM Usage</span>
                  <span className="text-white font-medium">80.5%</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs text-white/60 pl-4">
                  <div>+ Wired: 1.5 GB</div>
                  <div>+ Active: 1.5 GB</div>
                  <div>+ Compressed: 2.9 GB (HIGH)</div>
                  <div>+ Cached: 1.5 GB</div>
                </div>
              </div>
              
              <div className="mb-4 pb-4 border-b border-white/5">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/60">Swap Usage</span>
                  <span className="text-white font-medium">60.1%</span>
                </div>
              </div>
              
              <div className="mb-4 pb-4 border-b border-white/5">
                <div className="text-xs text-white/30 uppercase tracking-widest mb-2">SETTINGS</div>
                <div className="text-xs text-white/60">Thresholds: CPU 85% | MEM 80% | SWAP 20%</div>
              </div>
              
              <div className="mb-4">
                <div className="text-xs text-white/30 uppercase tracking-widest mb-2">TOP CPU PROCESSES:</div>
                <div className="space-y-1 text-xs text-white/60 pl-4">
                  <div>Cursor Helper (Renderer): 30.8%</div>
                  <div>Cursor: 8.2%</div>
                  <div>Cursor Helper (GPU) [GPU]: 4.9%</div>
                </div>
              </div>
              
              <div>
                <div className="text-xs text-white/30 uppercase tracking-widest mb-2">TOP MEMORY PROCESSES:</div>
                <div className="space-y-1 text-xs text-white/60 pl-4">
                  <div>Cursor Helper (Renderer): 6.3%</div>
                  <div>Cursor Helper (Plugin): 2.3%</div>
                  <div>Cursor: 2.0%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-8 border-t border-black/10 dark:border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-light mb-4">Features</h2>
            <p className="text-black/60 dark:text-white/40">Everything you need for system monitoring on macOS</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureItem 
              title="Real-Time Monitoring"
              description="Track CPU, RAM, and Swap usage with high precision. Updates every 5 seconds."
            />
            <FeatureItem 
              title="Memory Breakdown"
              description="Detailed macOS memory analysis: Wired, Active, Compressed, and Cached states."
            />
            <FeatureItem 
              title="Process Intelligence"
              description="Identify top CPU and Memory processes. View which applications are consuming resources."
            />
            <FeatureItem 
              title="Threat Detection"
              description="Automatic alerts for high resource usage, memory pressure, and system lag risks."
            />
            <FeatureItem 
              title="Native Notifications"
              description="macOS notifications for critical system events. Configurable thresholds."
            />
            <FeatureItem 
              title="Menu Bar Integration"
              description="Clean, minimal interface that lives in your menu bar. No Dock icon, no distractions."
            />
          </div>
        </div>
      </section>

      {/* Technical Section - Redesigned with visual representation */}
      <section id="technical" className="py-24 px-8 border-t border-black/10 dark:border-white/5 bg-black/5 dark:bg-white/5">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-light mb-16 text-center">Technical Details</h2>
          
          <div className="grid md:grid-cols-2 gap-12 mb-16">
            {/* Menu Bar Status Display */}
            <div className="bg-black dark:bg-[#0a0a0a] border border-white/10 rounded-lg p-8">
              <div className="mb-6">
                <div className="text-xs text-white/30 uppercase tracking-widest mb-4">Menu Bar Status</div>
                <div className="text-2xl font-light text-white mb-2">STRESS! | CPU 18% | MEM 80%</div>
                <div className="text-sm text-white/60">Real-time status display in menu bar</div>
              </div>
            </div>

            {/* System Health Display */}
            <div className="bg-black dark:bg-[#0a0a0a] border border-white/10 rounded-lg p-8">
              <div className="mb-6">
                <div className="text-xs text-white/30 uppercase tracking-widest mb-4">System Health</div>
                <div className="text-2xl font-light text-white mb-2">NORMAL Pressure | STRESSED</div>
                <div className="text-sm text-white/60">Memory pressure and lag risk detection</div>
              </div>
            </div>
          </div>

          {/* Technical Specifications Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            <TechSpec 
              title="Resource Analysis"
              items={[
                "Detailed CPU thread tracking",
                "Swap file activity monitoring",
                "Direct macOS system API access",
                "Low-level resource hooks"
              ]}
            />
            <TechSpec 
              title="macOS Integration"
              items={[
                "AppKit Accessory Policy (no Dock icon)",
                "Native Notification Center integration",
                "vm_stat and sysctl API usage",
                "Apple Silicon optimized"
              ]}
            />
            <TechSpec 
              title="Architecture"
              items={[
                "Process ID (PID) mapping",
                "Dynamic alert thresholds",
                "Minimal memory footprint (<20MB)",
                "Python-powered with native bindings"
              ]}
            />
          </div>

          {/* Visual System Breakdown */}
          <div className="mt-16 bg-black dark:bg-[#0a0a0a] border border-white/10 rounded-lg p-8">
            <div className="text-xs text-white/30 uppercase tracking-widest mb-6">System Resource Breakdown</div>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <div className="text-sm text-white/60 mb-3">CPU Load</div>
                <div className="text-2xl font-light text-white mb-4">17.9% (NORMAL)</div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: '17.9%' }}></div>
                </div>
              </div>
              <div>
                <div className="text-sm text-white/60 mb-3">RAM Usage</div>
                <div className="text-2xl font-light text-white mb-4">80.5%</div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-yellow-500" style={{ width: '80.5%' }}></div>
                </div>
              </div>
              <div>
                <div className="text-sm text-white/60 mb-3">Memory Breakdown</div>
                <div className="space-y-2 text-xs text-white/60">
                  <div className="flex justify-between">
                    <span>Wired</span>
                    <span className="text-white">1.5 GB</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active</span>
                    <span className="text-white">1.5 GB</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Compressed</span>
                    <span className="text-yellow-400">2.9 GB (HIGH)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cached</span>
                    <span className="text-white">1.5 GB</span>
                  </div>
                </div>
              </div>
              <div>
                <div className="text-sm text-white/60 mb-3">Top Processes</div>
                <div className="space-y-2 text-xs text-white/60">
                  <div>Cursor Helper (Renderer): 30.8%</div>
                  <div>Cursor: 8.2%</div>
                  <div>Cursor Helper (GPU): 4.9%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Installation Section */}
      <section className="py-24 px-8 border-t border-black/10 dark:border-white/5">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-light mb-8 text-center">Installation</h2>
          
          <div className="bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 p-8">
            <div className="mb-6">
              <div className="text-xs text-black/30 dark:text-white/30 uppercase tracking-widest mb-2">Quick Start</div>
            </div>
            
            <div className="space-y-4 font-mono text-sm text-black/80 dark:text-white/80">
              <div>
                <div className="text-black/40 dark:text-white/40 mb-1"># Clone the repository</div>
                <div>git clone https://github.com/dinexh/Monarx.git</div>
                <div>cd Monarx</div>
              </div>
              
              <div>
                <div className="text-black/40 dark:text-white/40 mb-1"># Create virtual environment</div>
                <div>python3 -m venv .venv</div>
                <div>source .venv/bin/activate</div>
              </div>
              
              <div>
                <div className="text-black/40 dark:text-white/40 mb-1"># Install dependencies</div>
                <div>pip install psutil rumps pyobjc</div>
              </div>
              
              <div>
                <div className="text-black/40 dark:text-white/40 mb-1"># Run the application</div>
                <div>python main.py</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-8 border-t border-black/10 dark:border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8 text-sm text-black/40 dark:text-white/40">
          <div>
            <span>Monarx</span>
          </div>
          <div>© 2026 Monarx. Designed and developed by <a href="https://dineshkorukonda.in" className="hover:text-black dark:hover:text-white transition-colors">Dinesh Korukonda</a>.</div>
        </div>
      </footer>
    </div>
  );
}

function FeatureItem({ title, description }: { title: string, description: string }) {
  return (
    <div className="border-b border-black/10 dark:border-white/5 pb-8">
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      <p className="text-black/60 dark:text-white/40 text-sm leading-relaxed">
        {description}
      </p>
    </div>
  );
}

function TechSpec({ title, items }: { title: string, items: string[] }) {
  return (
    <div>
      <h3 className="text-sm uppercase tracking-widest text-black/30 dark:text-white/30 mb-4">{title}</h3>
      <ul className="space-y-3 text-black/60 dark:text-white/60">
        {items.map((item, i) => (
          <li key={i} className="text-sm">• {item}</li>
        ))}
      </ul>
    </div>
  );
}
