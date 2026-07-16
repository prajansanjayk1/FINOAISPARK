import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Governance Platform | Mission Control",
  description: "Enterprise AI Governance Platform for Banking Security",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased bg-background text-foreground h-screen flex overflow-hidden`}
      >
        <Sidebar />
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <TopNav />
          <main className="flex-1 overflow-y-auto p-8 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-primary/[0.02] to-transparent -z-10 pointer-events-none" />
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
