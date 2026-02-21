"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiGet, apiPost } from "@/lib/api";

export default function StartScan() {
  const [datasources, setDatasources] = useState<any[]>([]);
  const [dataSourceId, setDataSourceId] = useState<number>(0);
  const [sampleSize, setSampleSize] = useState<number>(500);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet("/datasources").then((ds)=> {
      setDatasources(ds);
      if (ds.length) setDataSourceId(ds[0].id);
    }).catch((e)=>setErr(String(e)));
  }, []);

  async function start() {
    setErr("");
    try {
      const r = await apiPost("/scans", { data_source_id: dataSourceId, mode: "quick", sample_size: sampleSize });
      window.location.href = `/scans/${r.scan_run_id}`;
    } catch (e:any) {
      setErr(String(e));
    }
  }

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Scan Setup</h1>
      <p style={{ color:"#9EA9B6" }}>Pick datasource + sample size. MVP runs synchronously.</p>
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      <div style={{ display:"flex", gap:12, alignItems:"center" }}>
        <label>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>Datasource</div>
          <select value={dataSourceId} onChange={(e)=>setDataSourceId(Number(e.target.value))}
            style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5" }}>
            {datasources.map((d)=> <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </label>

        <label>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>Sample size / table</div>
          <input value={sampleSize} onChange={(e)=>setSampleSize(Number(e.target.value))}
            style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", width:160 }} />
        </label>

        <button onClick={start} style={{ marginTop:18, padding:"10px 12px", borderRadius:10, border:"1px solid #22C55E", background:"transparent", color:"#E9EEF5" }}>
          Start Scan
        </button>
      </div>
    </Shell>
  );
}
