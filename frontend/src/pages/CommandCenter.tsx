import React, { useEffect, useState, useRef } from 'react';
import { Terminal as TerminalIcon, Shield, Activity, Wifi } from 'lucide-react';

interface LogEntry {
  type: string;
  sender?: string;
  content?: string;
  agent?: string;
  message?: string;
  timestamp: string;
}

export const CommandCenter = ({ password }: { password: string }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use the same host but port 8000 for backend if on dev, or same host/port if in prod
    const host = window.location.hostname === 'localhost' ? 'localhost:8000' : window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/ws/logs?password=${password}`);

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => setStatus('disconnected');
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLogs((prev) => [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }].slice(-50));
      } catch (e) {
        console.error("Failed to parse log message:", e);
      }
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const renderLog = (log: LogEntry, index: number) => {
    const baseStyle = "py-1 px-2 mb-1 rounded text-[11px] font-mono leading-tight";
    
    switch (log.type) {
      case 'incoming_message':
        return (
          <div key={index} className={`${baseStyle} bg-blue-900/20 border-l-2 border-blue-500 text-blue-100`}>
            <span className="text-blue-400 font-bold">[{log.timestamp}] INCOMING_MSG </span>
            <span className="text-gray-500 italic">from:{log.sender}</span>
            <div className="mt-1 opacity-90">{log.content}</div>
          </div>
        );
      case 'routing':
        return (
          <div key={index} className={`${baseStyle} bg-purple-900/20 border-l-2 border-purple-500 text-purple-100`}>
            <span className="text-purple-400 font-bold">[{log.timestamp}] AGENT_ROUTE </span>
            <span className="bg-purple-500/30 px-1 rounded">{log.agent}</span>
          </div>
        );
      case 'outgoing_message':
        return (
          <div key={index} className={`${baseStyle} bg-green-900/20 border-l-2 border-green-500 text-green-100`}>
            <span className="text-green-400 font-bold">[{log.timestamp}] OUTGOING_MSG </span>
            <div className="mt-1 opacity-90">{log.content}</div>
          </div>
        );
      case 'thought':
        return (
          <div key={index} className={`${baseStyle} bg-yellow-900/10 border-l-2 border-yellow-600/50 text-yellow-100/80`}>
            <span className="text-yellow-600 font-bold">[{log.timestamp}] AGENT_THOUGHT </span>
            <div className="mt-1 italic opacity-70">{log.content}</div>
          </div>
        );
      case 'error':
        return (
          <div key={index} className={`${baseStyle} bg-red-900/20 border-l-2 border-red-500 text-red-100`}>
            <span className="text-red-400 font-bold">[{log.timestamp}] SYSTEM_ERROR </span>
            <div className="mt-1">{log.message}</div>
          </div>
        );
      default:
        return (
          <div key={index} className={`${baseStyle} bg-gray-800/40 text-gray-400`}>
            <span className="font-bold">[{log.timestamp}] {log.type.toUpperCase()} </span>
            <pre className="mt-1 whitespace-pre-wrap">{JSON.stringify(log, null, 2)}</pre>
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col h-full font-mono">
      <div className="flex items-center justify-between mb-4 bg-gray-900/50 p-2 border border-gray-800 rounded">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Activity size={14} className="text-blue-400" />
            <span className="text-xs font-bold text-gray-400">SYSTEM_STREAM</span>
          </div>
          <div className={`flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${
            status === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            <Wifi size={10} />
            <span>{status}</span>
          </div>
        </div>
        <div className="text-[10px] text-gray-600 uppercase">
          Build: 0.1.0-ALPHA
        </div>
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto bg-black/40 border border-gray-800 rounded p-2 custom-scrollbar min-h-[300px]"
      >
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-700 opacity-50">
            <TerminalIcon size={48} className="mb-4" />
            <div className="text-xs uppercase tracking-widest">Awaiting system events...</div>
          </div>
        ) : (
          logs.map((log, i) => renderLog(log, i))
        )}
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-gray-900/30 border border-gray-800 p-3 rounded">
          <div className="flex items-center space-x-2 mb-1 text-gray-500">
            <Shield size={12} />
            <span className="text-[10px] font-bold uppercase tracking-tight">Security_Status</span>
          </div>
          <div className="text-lg font-bold text-green-500/80 tracking-tighter">ENCRYPTED</div>
        </div>
        <div className="bg-gray-900/30 border border-gray-800 p-3 rounded">
          <div className="flex items-center space-x-2 mb-1 text-gray-500">
            <Activity size={12} />
            <span className="text-[10px] font-bold uppercase tracking-tight">Active_Handlers</span>
          </div>
          <div className="text-lg font-bold text-blue-500/80 tracking-tighter">04_AGENTS</div>
        </div>
        <div className="bg-gray-900/30 border border-gray-800 p-3 rounded">
          <div className="flex items-center space-x-2 mb-1 text-gray-500">
            <Wifi size={12} />
            <span className="text-[10px] font-bold uppercase tracking-tight">Buffer_Load</span>
          </div>
          <div className="text-lg font-bold text-purple-500/80 tracking-tighter">{logs.length}/50</div>
        </div>
      </div>
    </div>
  );
};
