import React, { useState } from 'react'
import WhatsAppConnect from './components/WhatsAppConnect.jsx'
import MediaTemplateSender from './components/MediaTemplateSender.jsx'
import Inbox from './components/Inbox.jsx'
export default function App(){ const [tab,setTab]=useState('settings'); const tabBtn=(id,l)=>(<button onClick={()=>setTab(id)} className={`px-4 py-2 rounded-xl border border-white/10 ${tab===id?'bg-white/20':'bg-white/10'} hover:bg-white/20`}>{l}</button>); return (<div className='min-h-screen p-6 bg-gradient-to-b from-gray-950 via-gray-900 to-black'><h1 className='text-2xl font-bold mb-4'>WhatsApp Connector Admin</h1><div className='flex gap-2 mb-6'>{tabBtn('settings','Settings')}{tabBtn('send','Send')}{tabBtn('inbox','Inbox')}</div>{tab==='settings'&&<WhatsAppConnect/>}{tab==='send'&&<MediaTemplateSender/>}{tab==='inbox'&&<Inbox/>}</div>)}
