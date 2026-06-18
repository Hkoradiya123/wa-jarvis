import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { MemoryVault } from './pages/MemoryVault';
import { CommandCenter } from './pages/CommandCenter';
import { Reminders } from './pages/Reminders';
import { DirectConsole } from './pages/DirectConsole';
import { PromptManager } from './pages/PromptManager';
import { SystemStatus } from './pages/SystemStatus';
import { LoginPage } from './pages/LoginPage';

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));

  const handleLogin = (pass: string) => {
    localStorage.setItem('dashboard_password', pass);
    setPassword(pass);
  };

  if (!password) {
    return <LoginPage onLogin={handleLogin} />;
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
        {activeTab === 'prompts' && <PromptManager password={password} />}
        {activeTab === 'status' && <SystemStatus password={password} />}
      </div>
    </Layout>
  );
}

export default App;
