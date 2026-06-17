import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { MemoryVault } from './pages/MemoryVault';
import { CommandCenter } from './pages/CommandCenter';
import { Reminders } from './pages/Reminders';
import { DirectConsole } from './pages/DirectConsole';

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));
  const [tempPass, setTempPass] = useState('');

  if (!password) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-gray-300 flex items-center justify-center font-mono">
        <div className="border border-gray-800 p-8 rounded bg-[#161b22] w-96">
          <h1 className="text-blue-500 font-bold mb-4 tracking-widest text-sm">JARVIS_OS_LOGIN</h1>
          <input
            type="password"
            placeholder="ENTER_PASSWORD..."
            value={tempPass}
            onChange={(e) => setTempPass(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                localStorage.setItem('dashboard_password', tempPass);
                setPassword(tempPass);
              }
            }}
            className="w-full bg-black border border-gray-800 rounded px-3 py-2 text-xs focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => {
              localStorage.setItem('dashboard_password', tempPass);
              setPassword(tempPass);
            }}
            className="mt-4 w-full bg-blue-900/20 text-blue-500 border border-blue-900/50 py-2 text-[10px] hover:bg-blue-900/30"
          >
            ACCESS_SYSTEM
          </button>
        </div>
      </div>
    );
  }

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      <header className="mb-6 flex justify-between items-center">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-tighter">
          Root / {activeTab}
        </h2>
        <button 
          onClick={() => { localStorage.removeItem('dashboard_password'); setPassword(null); }}
          className="text-[10px] text-gray-600 hover:text-red-500"
        >
          LOGOUT
        </button>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <CommandCenter password={password} />}
        {activeTab === 'memory' && <MemoryVault password={password} />}
        {activeTab === 'reminders' && <Reminders password={password} />}
        {activeTab === 'console' && <DirectConsole password={password} />}
      </div>
    </Layout>
  );
}

export default App;
