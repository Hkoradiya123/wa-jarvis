import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { MemoryVault } from './pages/MemoryVault';
import { CommandCenter } from './pages/CommandCenter';
import { Reminders } from './pages/Reminders';
import { DirectConsole } from './pages/DirectConsole';
import { PromptManager } from './pages/PromptManager';
import { SystemStatus } from './pages/SystemStatus';
import { UserManagement } from './pages/UserManagement';
import { LoginPage } from './pages/LoginPage';

interface LogEntry {
  type: string;
  sender?: string;
  content?: string;
  agent?: string;
  message?: string;
  timestamp: string;
}

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [username, setUsername] = useState<string | null>(localStorage.getItem('dashboard_user'));
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [wsStatus, setWsStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');

  useEffect(() => {
    if (!username || !password) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname === 'localhost' ? 'localhost:7860' : window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/ws/logs?username=${username}&password=${password}`);

    setWsStatus('connecting');

    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLogs((prev) => [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }].slice(-50));
      } catch (e) {
        console.error("Failed to parse log message:", e);
      }
    };

    return () => ws.close();
  }, [username, password]);

  const handleLogin = (user: string, pass: string) => {
    localStorage.setItem('dashboard_user', user);
    localStorage.setItem('dashboard_password', pass);
    setUsername(user);
    setPassword(pass);
  };

  if (!username || !password) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const authProps = { username: username!, password: password! };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      <header className="mb-6 flex justify-between items-center">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-tighter">
          Root / {activeTab}
        </h2>
        <div className="flex items-center space-x-4">
          <span className="text-[10px] text-blue-500 font-bold uppercase">ID: {username}</span>
          <button 
            onClick={() => { 
              localStorage.removeItem('dashboard_user');
              localStorage.removeItem('dashboard_password'); 
              setUsername(null);
              setPassword(null); 
              setLogs([]);
            }}
            className="text-[10px] text-gray-600 hover:text-red-500"
          >
            LOGOUT
          </button>
        </div>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <CommandCenter {...authProps} logs={logs} wsStatus={wsStatus} />}
        {activeTab === 'memory' && <MemoryVault {...authProps} />}
        {activeTab === 'reminders' && <Reminders {...authProps} />}
        {activeTab === 'console' && <DirectConsole {...authProps} />}
        {activeTab === 'prompts' && <PromptManager {...authProps} />}
        {activeTab === 'status' && <SystemStatus {...authProps} />}
        {activeTab === 'users' && <UserManagement {...authProps} />}
      </div>
    </Layout>
  );
}

export default App;

