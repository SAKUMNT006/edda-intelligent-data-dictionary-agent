"use client";
import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import { apiGet } from "@/lib/api";

type Tab = "columns" | "relationships" | "quality" | "docs";

export default function TablePage({ params }: { params: { tableId: string } }) {
  const tableId = Number(params.tableId);
  const [tab, setTab] = useState<Tab>("columns");
  const [table, setTable] = useState<any>(null);
  const [cols, setCols] = useState<any[]>([]);
  const [rels, setRels] = useState<any[]>([]);
  const [quality, setQuality] = useState<any>(null);
  const [docs, setDocs] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet(`/tables/${tableId}`).then(setTable).catch((e)=>setErr(String(e)));
  }, [tableId]);

  useEffect(() => {
    setErr("");
    if (tab === "columns") apiGet(`/tables/${tableId}/columns`).then(setCols).catch((e)=>setErr(String(e)));
    if (tab === "relationships") apiGet(`/tables/${tableId}/relationships`).then(setRels).catch((e)=>setErr(String(e)));
    if (tab === "quality") apiGet(`/tables/${tableId}/quality`).then(setQuality).catch((e)=>setErr(String(e)));
    if (tab === "docs") apiGet(`/tables/${tableId}/docs`).then(setDocs).catch((e)=>setErr(String(e)));
  }, [tab, tableId]);

  return (
    <Shell>
      <h1 style={{ fontSize:28, marginTop:0 }}>Table</h1>
      {err && <pre style={{ color:"#FBBF24" }}>{err}</pre>}

      {table && (
        <div style={{ border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
          <div style={{ fontWeight:800 }}>{table.schema_name}.{table.table_name}</div>
          <div style={{ color:"#9EA9B6", fontSize:12 }}>row_estimate: {table.row_estimate ?? "--"}</div>
        </div>
      )}

      <div style={{ display:"flex", gap:10, marginTop:12 }}>
        {(["columns","relationships","quality","docs"] as Tab[]).map((t)=> (
          <button key={t} onClick={()=>setTab(t)} style={{
            padding:"8px 10px", borderRadius:10,
            border:`1px solid ${tab===t ? "#38BDF8" : "#374151"}`,
            background:"transparent", color:"#E9EEF5"
          }}>{t}</button>
        ))}
      </div>

      {tab==="columns" && (
        <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
          <h3 style={{ marginTop:0 }}>Columns</h3>
          <table style={{ width:"100%", borderCollapse:"collapse" }}>
            <thead>
              <tr style={{ color:"#9EA9B6", fontSize:12, textAlign:"left" }}>
                <th>Name</th><th>Type</th><th>Nullable</th><th>PK</th><th>FK</th><th>PII</th>
              </tr>
            </thead>
            <tbody>
              {cols.map(c => (
                <tr key={c.id} style={{ borderTop:"1px solid #30363d" }}>
                  <td style={{ padding:"8px 0" }}>{c.column_name}</td>
                  <td>{c.data_type}</td>
                  <td>{String(c.nullable)}</td>
                  <td>{c.is_pk ? "PK" : ""}</td>
                  <td>{c.is_fk ? "FK" : ""}</td>
                  <td>{c.pii_risk || ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab==="relationships" && (
        <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
          <h3 style={{ marginTop:0 }}>Relationships</h3>
          <ul>
            {rels.map((r, i)=> (
              <li key={i} style={{ marginBottom:8 }}>
                {r.from} → {r.to} {r.constraint_name ? `(${r.constraint_name})` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab==="quality" && quality && (
        <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
          <h3 style={{ marginTop:0 }}>Quality</h3>
          <div>Quality score: <b>{quality.quality_score ?? "--"}</b></div>
          {quality.reasons?.length ? (
            <>
              <div style={{ marginTop:8, color:"#9EA9B6" }}>Warnings:</div>
              <ul>{quality.reasons.map((x:string, i:number)=> <li key={i}>{x}</li>)}</ul>
            </>
          ) : null}
          <pre style={{ marginTop:12, whiteSpace:"pre-wrap" }}>{JSON.stringify(quality.table_metrics, null, 2)}</pre>
        </div>
      )}

      {tab==="docs" && docs && (
        <div style={{ marginTop:12, border:"1px solid #374151", borderRadius:12, padding:12, background:"#161B22" }}>
          <h3 style={{ marginTop:0 }}>Docs (Markdown)</h3>
          <pre style={{ whiteSpace:"pre-wrap" }}>{docs.doc_markdown}</pre>
        </div>
      )}
    </Shell>
  );
}
