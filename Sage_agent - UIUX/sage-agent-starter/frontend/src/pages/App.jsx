import React, { useEffect, useState } from 'react'

function Section({title, children}){
  return (<div style={{border:'1px solid #222', borderRadius:8, padding:16, marginBottom:16}}>
    <h2 style={{marginTop:0}}>{title}</h2>
    {children}
  </div>)
}

export default function App(){
  const [wsDefaults, setWsDefaults] = useState({})
  const [newDefaults, setNewDefaults] = useState({ currency: 'ZAR', vatCode: 'ZA_STANDARD', paymentTerms: '30_days' })
  const [invoices, setInvoices] = useState([])

  useEffect(()=>{
    fetch('/api/settings/workspace').then(r=>r.json()).then(setWsDefaults).catch(()=>{})
  }, [])

  const saveDefaults = async () => {
    await fetch('/api/settings/workspace/invoice_defaults', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newDefaults)
    })
    const updated = await fetch('/api/settings/workspace').then(r=>r.json())
    setWsDefaults(updated)
  }

  const loadInvoices = async () => {
    const data = await fetch('/api/sage/sales_invoices').then(r=>r.json())
    setInvoices(data?.$items || data?.items || [])
  }

  return (
    <div style={{maxWidth: 1000, margin:'40px auto', fontFamily: 'Inter, system-ui, Arial'}}>
      <h1>AI Sage Agent (Starter)</h1>
      <p>This is a minimal UI to test settings and invoice listing against the backend connector.</p>

      <Section title="Connection">
        <a href="/auth/start"><button>Connect Sage (OAuth)</button></a>
        <span style={{marginLeft:12}}><a href="/healthz">Backend health</a></span>
      </Section>

      <Section title="Workspace Defaults">
        <div style={{display:'flex', gap:12}}>
          <label>Currency: <input value={newDefaults.currency} onChange={e=>setNewDefaults(d=>({...d, currency:e.target.value}))}/></label>
          <label>VAT Code: <input value={newDefaults.vatCode} onChange={e=>setNewDefaults(d=>({...d, vatCode:e.target.value}))}/></label>
          <label>Terms: <input value={newDefaults.paymentTerms} onChange={e=>setNewDefaults(d=>({...d, paymentTerms:e.target.value}))}/></label>
          <button onClick={saveDefaults}>Save</button>
        </div>
        <pre style={{background:'#111', color:'#ddd', padding:12, borderRadius:8}}>{JSON.stringify(wsDefaults, null, 2)}</pre>
      </Section>

      <Section title="Sales Invoices (Read)">
        <button onClick={loadInvoices}>Load Invoices</button>
        <div style={{marginTop:12}}>
          {invoices.length === 0 ? <p>No invoices loaded yet.</p> : (
            <table width="100%" cellPadding="6" style={{borderCollapse:'collapse'}}>
              <thead><tr><th align="left">ID</th><th align="left">Number</th><th align="left">Contact</th><th align="left">Total</th><th align="left">Updated</th></tr></thead>
              <tbody>
                {invoices.map((inv, i)=> (
                  <tr key={i} style={{borderTop:'1px solid #333'}}>
                    <td>{inv.id || inv['$uuid']}</td>
                    <td>{inv.displayed_as || inv.reference || '-'}</td>
                    <td>{inv.contact?.displayed_as || inv.customer?.name || '-'}</td>
                    <td>{inv.total || inv.gross_total || '-'}</td>
                    <td>{inv.updated_at || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </Section>
    </div>
  )
}
