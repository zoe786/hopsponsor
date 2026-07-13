"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const CORE_NAV = [
  { label: "Dashboard", icon: "📊", href: "/" },
  { label: "Sponsors", icon: "👥", href: "/sponsors" },
  { label: "Students", icon: "🎓", href: "/students" },
  { label: "Messages", icon: "✉️", href: "/messages" },
  { label: "Reports", icon: "📁", href: "/reports" },
  { label: "Schedule", icon: "🗓️", href: "/schedule" },
  { label: "Payments", icon: "💳", href: "/payments" },
  { label: "Calendar", icon: "📅", href: "/calendar" },
];

const INTEL_NAV = [
  { label: "AI Intelligence", icon: "🧠", href: "/ai" },
  { label: "Style Library", icon: "🎨", href: "/style-library" },
  { label: "Message History", icon: "📜", href: "/message-history" },
];

interface Stats {
  sponsors: number;
  students: number;
}

export function Sidebar() {
  const pathname = usePathname();
  const [stats, setStats] = useState<Stats>({ sponsors: 0, students: 0 });

  useEffect(() => {
    fetch("/api/dashboard")
      .then((r) => r.json())
      .then((d) => {
        if (d.success) {
          setStats({ sponsors: d.data.totalSponsors, students: d.data.totalStudents });
        }
      })
      .catch(() => {});
  }, [pathname]);

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-brand-icon">✦</span>
        <span><span className="accent">HOP</span>e</span>
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-stats">
        <div className="sidebar-stat">
          <div className="sidebar-stat-label">Sponsors</div>
          <div className="sidebar-stat-value">{stats.sponsors}</div>
        </div>
        <div className="sidebar-stat green">
          <div className="sidebar-stat-label">Students</div>
          <div className="sidebar-stat-value">{stats.students}</div>
        </div>
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section-label">CORE</div>
      <nav>
        {CORE_NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? "active" : ""}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div style={{ marginTop: "0.5rem" }} />

      <div className="sidebar-section-label">INTELLIGENCE</div>
      <nav>
        {INTEL_NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? "active" : ""}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div style={{ marginTop: "auto" }}>
        <div className="sidebar-divider" />
        <div style={{ padding: "0.3rem 0.9rem", fontSize: "0.75rem", color: "#4B5563" }}>
          HOPe Sponsor Assistant
        </div>
      </div>
    </aside>
  );
}
