"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiGet } from "@/lib/api";

export default function History() {
  const [scans, setScans] = useState<any[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet("/scans/recent").then(setScans).catch((e)=>setErr(String(e)));
  }, []);

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>History</h1>
      <p style={{ color:"#9EA9B6" }}>Scan history (schema diff is a stretch feature).</p>
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      {scans.map(s => (
        <div key={s.id} style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:10 }}>
          <div style={{ fontWeight:700 }}>Scan #{s.id} • {s.status}</div>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {s.schema_hash || "--"} • started: {s.started_at}</div>
        </div>
      ))}
    </Shell>
  );
}
