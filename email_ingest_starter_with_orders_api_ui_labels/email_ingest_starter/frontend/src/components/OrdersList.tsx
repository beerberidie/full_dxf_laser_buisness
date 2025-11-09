
import React, { useEffect, useState } from 'react'

export const OrdersList: React.FC = () => {
  const [orders, setOrders] = useState<any[]>([])
  const [busyId, setBusyId] = useState<number | null>(null)
  const load = async () => {
    const res = await fetch('http://localhost:8000/orders')
    const data = await res.json()
    setOrders(data)
  }
  useEffect(() => { load() }, [])

  const approveSend = async (emailId: number) => {
    setBusyId(emailId)
    try {
      const res = await fetch(`http://localhost:8000/emails/${emailId}/approve_send`, { method: 'POST' })
      if (!res.ok) throw new Error(await res.text())
      await load()
      alert('Sent!')
    } catch (e:any) {
      alert('Send failed: ' + e.message)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div style={{marginTop: 24}}>
      <h2>Recent Orders</h2>
      <div style={{border:'1px solid #ddd', borderRadius:12, overflow:'hidden'}}>
        <table style={{width:'100%', borderCollapse:'collapse'}}>
          <thead>
            <tr style={{background:'#f6f6f6'}}>
              <th style={{textAlign:'left', padding:8}}>ID</th>
              <th style={{textAlign:'left', padding:8}}>PO</th>
              <th style={{textAlign:'left', padding:8}}>Due</th>
              <th style={{textAlign:'left', padding:8}}>Route</th>
              <th style={{textAlign:'left', padding:8}}>Items</th>
              <th style={{textAlign:'left', padding:8}}>Draft</th>
              <th style={{textAlign:'left', padding:8}}>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => (
              <tr key={o.id}>
                <td style={{padding:8}}>{o.id}</td>
                <td style={{padding:8}}>{o.po_number || '-'}</td>
                <td style={{padding:8}}>{o.due_date || '-'}</td>
                <td style={{padding:8}}>{o.route_label || '-'}</td>
                <td style={{padding:8}}>
                  {o.items?.map((it:any) => `${it.quantity}× ${it.description}`).join('; ')}
                </td>
                <td style={{padding:8}}>{o.draft_status || '-'}</td>
                <td style={{padding:8}}>
                  {o.email_id && o.draft_status === 'draft' ? (
                    <button
                      onClick={() => approveSend(o.email_id)}
                      disabled={busyId === o.email_id}
                      style={{padding:'6px 10px', borderRadius:8, border:'1px solid #333', background:'#fff'}}
                    >
                      {busyId === o.email_id ? 'Sending…' : 'Approve & Send'}
                    </button>
                  ) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
