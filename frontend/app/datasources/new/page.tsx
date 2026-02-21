"use client";
import { useState } from "react";
import Shell from "@/components/Shell";
import { apiPost } from "@/lib/api";

export default function NewDatasource() {
  const [form, setForm] = useState<any>({
    name: "demo_db",
    db_type: "postgres",
    host: "localhost",
    port: 5433,
    database: "demo",
    schema: "public",
    username: "demo",
    password: "demo"
  });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  async function testConn() {
    setErr(""); setMsg("Testing...");
    try { await apiPost("/datasources/test", form); setMsg("Connection looks good."); }
    catch (e:any) { setErr(String(e)); setMsg(""); }
  }

  async function save() {
    setErr(""); setMsg("Saving...");
    try { const r = await apiPost("/datasources", form); setMsg(`Saved datasource id=${r.id}`); }
    catch (e:any) { setErr(String(e)); setMsg(""); }
  }

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Add Data Source</h1>
      <p style={{ color:"#9EA9B6" }}>Use read-only credentials for real DBs. Demo DB works out-of-box.</p>
      {msg && <div style={{ color:"#22C55E" }}>{msg}</div>}
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      <div style={{ display:"grid", gridTemplateColumns:"repeat(2, minmax(0,1fr))", gap:10 }}>
        {Object.entries(form).map(([k,v]) => (
          <label key={k} style={{ display:"flex", flexDirection:"column", gap:6 }}>
            <span style={{ color:"#9EA9B6", fontSize:12 }}>{k}</span>
            <input value={String(v)}
              onChange={(e)=>setForm((p:any)=>({ ...p, [k]: k==="port" ? Number(e.target.value) : e.target.value }))}
              style={{ padding:10, borderRadius:10, border:"1px solid #374151", background:"#161B22", color:"#E9EEF5" }}
            />
          </label>
        ))}
      </div>

      <div style={{ display:"flex", gap:10, marginTop:14 }}>
        <button onClick={testConn} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #38BDF8", background:"transparent", color:"#E9EEF5" }}>
          Test Connection
        </button>
        <button onClick={save} style={{ padding:"10px 12px", borderRadius:10, border:"1px solid #22C55E", background:"transparent", color:"#E9EEF5" }}>
          Save
        </button>
      </div>
    </Shell>
  );
}
