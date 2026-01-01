import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Monarx | macOS System Monitor",
  description: "Real-time resource monitoring, process intelligence, and system health alerts for macOS.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth dark">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
