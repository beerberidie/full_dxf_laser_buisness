import React, { useState } from "react";
import { useChat } from "../lib/useChat";

export default function AIChatBox(){
  const { output, loading, send } = useChat();
  const [input, setInput] = useState("");
  return (
    <div className="p-4 rounded-2xl shadow border">
      <div className="min-h-32 whitespace-pre-wrap">{output}</div>
      <div className="flex gap-2 mt-3">
        <input className="flex-1 border p-2 rounded"
               value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask the model..." />
        <button className="px-3 py-2 rounded bg-black text-white" disabled={loading} onClick={()=>send(input)}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
