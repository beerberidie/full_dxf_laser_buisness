import React, { useEffect, useState } from 'react'

export const MailboxConnect: React.FC = () => {
  return (
    <div style={{display:'grid', gap: 16}}>
      <h1 style={{fontSize: 24}}>Connect your mailbox</h1>
      <p>Choose a provider to connect your mailbox. We use read-only scopes by default and you can disconnect anytime.</p>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 16}}>
        <ProviderCard
          title="Connect Gmail"
          description="Use Gmail API + Pub/Sub for push delivery."
          href="http://localhost:8000/auth/gmail/start"
        />
        <ProviderCard
          title="Connect Outlook"
          description="Use Microsoft Graph subscriptions for push delivery."
          href="http://localhost:8000/auth/m365/start"
        />
      </div>
      <StatusHint />
    </div>
  )
}

const ProviderCard: React.FC<{title:string, description:string, href:string}> = ({title, description, href}) => {
  const [busy, setBusy] = useState(false)
  return (
    <div style={{border:'1px solid #ddd', borderRadius:12, padding:16}}>
      <h3 style={{marginTop:0}}>{title}</h3>
      <p style={{marginTop:8, color:'#444'}}>{description}</p>
      <a
        href={href}
        onClick={() => setBusy(true)}
        style={{
          display:'inline-block', padding:'8px 14px', borderRadius:10, border:'1px solid #333',
          textDecoration:'none'
        }}
      >
        {busy ? 'Redirecting…' : 'Connect'}
      </a>
    </div>
  )
}

const StatusHint: React.FC = () => (
  <div style={{padding:12, background:'#f8f8f8', border:'1px solid #eee', borderRadius:10}}>
    <strong>After connecting:</strong> you should see a simple "Connected" page from the backend. Configure webhooks with a public URL (e.g. ngrok) so Gmail/M365 can reach your server.
  </div>
)
