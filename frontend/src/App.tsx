import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { MemoryVault } from './pages/MemoryVault';
import { CommandCenter } from './pages/CommandCenter';
import { Reminders } from './pages/Reminders';
import { DirectConsole } from './pages/DirectConsole';
import { PromptManager } from './pages/PromptManager';
import { SystemStatus } from './pages/SystemStatus';
import { UserManagement } from './pages/UserManagement';
import { LoginPage } from './pages/LoginPage';

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [username, setUsername] = useState<string | null>(localStorage.getItem('dashboard_user'));
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));

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
            }}
            className="text-[10px] text-gray-600 hover:text-red-500"
          >
            LOGOUT
          </button>
        </div>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <CommandCenter {...authProps} />}
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
