import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "HOPe — Sponsor Assistant",
  description: "Sponsor relationship & student support dashboard",
  icons: { icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✨</text></svg>" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="app-layout">
          <Sidebar />
          <main className="main-content">
            {children}
          </main>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#1E1B4B",
              color: "#F1F5F9",
              border: "1px solid rgba(139,92,246,0.35)",
              borderRadius: "10px",
              fontSize: "0.875rem",
            },
            success: { iconTheme: { primary: "#34D399", secondary: "#1E1B4B" } },
            error:   { iconTheme: { primary: "#FCA5A5", secondary: "#1E1B4B" } },
          }}
        />
      </body>
    </html>
  );
}
