"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiGet } from "@/lib/api";

export default function ScanExplorer({ params }: { params: { scanId: string } }) {
  const scanId = Number(params.scanId);
  const [scan, setScan] = useState<any>(null);
  const [tables, setTables] = useState<any[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    Promise.all([apiGet(`/scans/${scanId}`), apiGet(`/tables?scan_run_id=${scanId}`)])
      .then(([s, t]) => { setScan(s); setTables(t); })
      .catch((e)=>setErr(String(e)));
  }, [scanId]);

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Schema Explorer</h1>
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      {scan && (
        <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22", marginBottom:12 }}>
          <div style={{ fontWeight:800 }}>Scan #{scan.id} • {scan.status}</div>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>schema_hash: {scan.schema_hash || "--"} • sample: {scan.sample_size}</div>
        </div>
      )}

      <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:10 }}>
        {tables.map((t)=> (
          <a key={t.id} href={`/tables/${t.id}`} style={{ textDecoration:"none", color:"#E9EEF5" }}>
            <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
              <div style={{ fontWeight:700 }}>{t.schema_name}.{t.table_name}</div>
              <div style={{ color:"#9EA9B6", fontSize:12 }}>row_estimate: {t.row_estimate ?? "--"}</div>
            </div>
          </a>
        ))}
      </div>
    </Shell>
  );
}
