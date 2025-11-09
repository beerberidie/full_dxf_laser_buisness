import React from 'react'
import { createRoot } from 'react-dom/client'
import { MailboxConnect } from './components/MailboxConnect'
import { OrdersList } from './components/OrdersList'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div style={{maxWidth: 800, margin: '40px auto', fontFamily: 'system-ui'}}>
      <MailboxConnect />
      <OrdersList />
    </div>
  </React.StrictMode>
)
