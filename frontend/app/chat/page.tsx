"use client";
import { useState } from "react";
import Shell from "@/components/Shell";
import { apiPost } from "@/lib/api";

export default function Chat() {
  const [scanRunId, setScanRunId] = useState<number>(1);
  const [q, setQ] = useState("How do I join orders to payments?");
  const [out, setOut] = useState<any>(null);
  const [err, setErr] = useState("");

  async function ask() {
    setErr("");
    try {
      const r = await apiPost("/chat", { scan_run_id: scanRunId, question: q, include_sql: true });
      setOut(r);
    } catch (e:any) {
      setErr(String(e));
    }
  }

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Chat</h1>
      <p style={{ color:"#9EA9B6" }}>Ask schema questions grounded in stored docs/relationships.</p>

      <div style={{ display:"flex", gap:10, alignItems:"center" }}>
        <label>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>scan_run_id</div>
          <input value={scanRunId} onChange={(e)=>setScanRunId(Number(e.target.value))}
            style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", width:160 }} />
        </label>
        <button onClick={ask} style={{ marginTop:18, padding:"10px 12px", borderRadius:10, border:"1px solid #38BDF8", background:"transparent", color:"#E9EEF5" }}>
          Send
        </button>
      </div>

      <textarea value={q} onChange={(e)=>setQ(e.target.value)} rows={3}
        style={{ width:"100%", padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5", marginTop:10 }} />

      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}
      {out && <pre style={{ marginTop:12, padding:12, borderRadius:12, border:"1px solid #374151", background:"#161B22" }}>{JSON.stringify(out, null, 2)}</pre>}
    </Shell>
  );
}
