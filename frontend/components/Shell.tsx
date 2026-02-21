import Link from "next/link";

const nav = [
  { href: "/", label: "Home" },
  { href: "/datasources/new", label: "Add Data Source" },
  { href: "/scans/new", label: "Start Scan" },
  { href: "/chat", label: "Chat" },
  { href: "/history", label: "History" }
];

export default function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display:"flex", minHeight:"100vh", background:"#0D1117", color:"#E9EEF5" }}>
      <aside style={{ width:240, padding:16, borderRight:"1px solid #374151" }}>
        <div style={{ fontSize:22, fontWeight:800, marginBottom:6 }}>EDDA</div>
        <div style={{ fontSize:12, color:"#9EA9B6", marginBottom:16 }}>Elephantidae Data Dictionary Agent</div>
        {nav.map(n => (
          <Link key={n.href} href={n.href} style={{
            display:"block", padding:"10px 12px", marginBottom:8, borderRadius:10,
            border:"1px solid #374151", color:"#E9EEF5", textDecoration:"none"
          }}>{n.label}</Link>
        ))}
      </aside>
      <main style={{ flex:1, padding:20 }}>{children}</main>
    </div>
  );
}
