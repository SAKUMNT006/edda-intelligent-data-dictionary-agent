"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiGet } from "@/lib/api";

export default function Home() {
  const [datasources, setDatasources] = useState<any[]>([]);
  const [scans, setScans] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([apiGet("/datasources"), apiGet("/scans/recent")])
      .then(([ds, sc]) => { setDatasources(ds); setScans(sc); })
      .catch(e => setErr(String(e)));
  }, []);

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Home</h1>
      <p style={{ color:"#9EA9B6" }}>Connect a database, scan it, and generate a trusted data dictionary.</p>
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      <h2 style={{ fontSize:18 }}>Data Sources</h2>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:12 }}>
        {datasources.map(d => (
          <div key={d.id} style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
            <div style={{ fontWeight:800 }}>{d.name}</div>
            <div style={{ color:"#9EA9B6", fontSize:12 }}>{d.db_type} • {d.host}:{d.port} • {d.database}</div>
          </div>
        ))}
      </div>

      <h2 style={{ fontSize:18, marginTop:18 }}>Recent Scans</h2>
      {scans.map(s => (
        <a key={s.id} href={`/scans/${s.id}`} style={{ textDecoration:"none", color:"#E9EEF5" }}>
          <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:10 }}>
            <div style={{ fontWeight:700 }}>Scan #{s.id} • {s.status}</div>
            <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {s.schema_hash || "--"} • sample: {s.sample_size}</div>
          </div>
        </a>
      ))}
    </Shell>
  );
}
