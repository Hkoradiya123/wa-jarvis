import React, { useState } from 'react';
import { Send, Terminal } from 'lucide-react';

export const DirectConsole = ({ username, password }: any) => {
  const [payload, setPayload] = useState(JSON.stringify({
    event: "message",
    data: {
      from: "user_test",
      body: "//jarvis help",
      fromMe: false
    }
  }, null, 2));
  const [status, setStatus] = useState<string | null>(null);

  const sendPayload = async () => {
    setStatus("SENDING...");
    try {
      const res = await fetch('/webhook', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: payload
      });
      const data = await res.json();
      setStatus(`SUCCESS: ${JSON.stringify(data)}`);
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  return (
    <div className="space-y-4 font-mono">
      <div className="flex items-center space-x-2 text-blue-500 mb-4">
        <Terminal size={14} />
        <h3 className="text-xs font-bold uppercase tracking-tighter">Webhook_Simulator</h3>
      </div>

      <div className="space-y-2">
        <label className="text-[10px] text-gray-500 font-bold">JSON_PAYLOAD</label>
        <textarea
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          rows={12}
          className="w-full bg-black border border-gray-800 rounded p-4 text-xs text-green-500 focus:outline-none focus:border-blue-500 font-mono leading-relaxed"
        />
      </div>

      <div className="flex justify-between items-center bg-gray-900/30 p-3 border border-gray-800 rounded">
        <div className="text-[10px] text-gray-400 truncate max-w-[70%] font-mono italic">
          {status ? `> ${status}` : "READY_FOR_EXECUTION"}
        </div>
        <button
          onClick={sendPayload}
          className="flex items-center space-x-2 bg-blue-900/20 text-blue-500 border border-blue-900/50 px-4 py-2 text-[10px] hover:bg-blue-900/30 transition-all font-bold uppercase tracking-widest"
        >
          <Send size={12} />
          <span>Execute</span>
        </button>
      </div>
    </div>
  );
};
