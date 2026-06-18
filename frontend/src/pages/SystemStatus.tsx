import React, { useEffect, useState } from 'react';
import { Database, Cpu, Globe, RefreshCw, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

interface SystemStatusProps {
  username: string;
  password: string;
}

export const SystemStatus = ({ username, password }: SystemStatusProps) => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/system/status', {
        headers: { 'X-Username': username, 'X-Password': password }
      });
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Failed to fetch system status:", e);
    }
    setLoading(false);
  };

  useEffect(() => { fetchStatus(); }, []);

  const getStatusColor = (val: string) => {
    if (val === 'online' || val === 'configured') return 'text-green-500 border-green-500/20 bg-green-500/5';
    if (val === 'offline' || val === 'missing') return 'text-red-500 border-red-500/20 bg-red-500/5';
    return 'text-yellow-500 border-yellow-500/20 bg-yellow-500/5';
  };

  const getStatusIcon = (val: string) => {
    if (val === 'online' || val === 'configured') return <CheckCircle2 size={16} />;
    if (val === 'offline' || val === 'missing') return <XCircle size={16} />;
    return <AlertTriangle size={16} />;
  };

  if (loading && !status) {
    return <div className="text-gray-500 animate-pulse">Scanning system peripherals...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center space-x-2">
          <Globe size={14} />
          <span>System_Health_Monitor</span>
        </h3>
        <button onClick={fetchStatus} className="text-gray-500 hover:text-white transition-colors">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`p-4 border rounded transition-all ${getStatusColor(status?.mongodb)}`}>
          <div className="flex items-center justify-between mb-4">
            <Database size={24} className="opacity-50" />
            {getStatusIcon(status?.mongodb)}
          </div>
          <div className="text-[10px] font-bold uppercase opacity-60 mb-1">Database_Node</div>
          <div className="text-sm font-mono font-bold tracking-tight">MongoDB_Cluster</div>
          <div className="mt-2 text-[10px] uppercase font-bold">{status?.mongodb}</div>
        </div>

        <div className={`p-4 border rounded transition-all ${getStatusColor(status?.nvidia_api)}`}>
          <div className="flex items-center justify-between mb-4">
            <Cpu size={24} className="opacity-50" />
            {getStatusIcon(status?.nvidia_api)}
          </div>
          <div className="text-[10px] font-bold uppercase opacity-60 mb-1">Intelligence_Core</div>
          <div className="text-sm font-mono font-bold tracking-tight">NVIDIA_NIM_API</div>
          <div className="mt-2 text-[10px] uppercase font-bold">{status?.nvidia_api}</div>
        </div>

        <div className={`p-4 border rounded transition-all ${getStatusColor(status?.openwa_gateway)}`}>
          <div className="flex items-center justify-between mb-4">
            <Globe size={24} className="opacity-50" />
            {getStatusIcon(status?.openwa_gateway)}
          </div>
          <div className="text-[10px] font-bold uppercase opacity-60 mb-1">Comm_Gateway</div>
          <div className="text-sm font-mono font-bold tracking-tight">Open-WA_Server</div>
          <div className="mt-2 text-[10px] uppercase font-bold">{status?.openwa_gateway}</div>
        </div>
      </div>

      <div className="bg-black/20 border border-gray-800 rounded p-4">
        <div className="text-[10px] font-bold text-gray-600 uppercase mb-2">Diagnostic_Summary</div>
        <div className="text-xs font-mono text-gray-400 leading-relaxed">
          {status?.mongodb === 'online' && status?.nvidia_api === 'configured' && status?.openwa_gateway === 'online' ? (
            <span className="text-green-900/80">All systems operational. Intelligence layers synchronized with communication gateways.</span>
          ) : (
            <span className="text-red-900/80">Degraded performance detected. Some subsystems are unresponsive or misconfigured. Manual intervention may be required.</span>
          )}
        </div>
      </div>
    </div>
  );
};
